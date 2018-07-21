<!--
    Breadcrumb vue component
    Breadcrumb mirrors the current router link
    Caches named view names in store
    Settings object allows aliasing of page names and creation of new named routes
-->

<template>
    <div class="breadcrumb-container">
        <b-row>
            <b-col cols="12" md="12">
                <h4>
                    <span v-for="crumb in crumbs.slice(0, -1)" :key="crumb.route">
                        <b-link tag="b-button" :to="{ name: crumb.routeName }">{{ crumb.displayName }}</b-link> /
                    </span>
                </h4>
                <h1>
                    {{ crumbs.slice(-1)[0].displayName }}
                    <slot>
                        <icon name="eye" @click.native="eyeClick()" class="eye-icon" scale="1.75"></icon>
                        <b-button v-if="canEdit()" @click="editClick()" class="float-right change-button"> Edit</b-button>
                    </slot>
                </h1>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import commonAPI from '@/api/common.js'
import icon from 'vue-awesome/components/Icon'
import store from '@/Store.vue'

export default {
    components: {
        icon
    },
    /*
        aliases: aliases for unnamed vews
        namedViews: list of named views, with associated data field in get_names and primary parameter
    */
    data () {
        return {
            settings: {
                aliases: {
                    'Home': 'Courses',
                    'FormatEdit': 'Format Editor',
                    'CourseEdit': 'Course Editor',
                    'AssignmentEdit': 'Assignment Editor',
                    'AssignmentsOverview': 'Assignment Overview',
                    'UserRoleConfiguration': 'User Role Configuration'
                },
                namedViews: {
                    'Course': { apiReturnValue: 'course', primaryParam: 'cID' },
                    'Assignment': { apiReturnValue: 'assignment', primaryParam: 'aID' },
                    'Journal': { apiReturnValue: 'journal', primaryParam: 'jID' }
                }
            },
            cachedMap: {},
            crumbs: []
        }
    },
    methods: {
        // Match routes that prepend the current path, create incomplete crumbs
        findRoutes () {
            var routeMatched = this.$route.matched[0].path
            var routerRoutes = this.$router.options.routes
            routerRoutes.sort((a, b) => a.path.length - b.path.length)

            // Add every matched (sub)route with params substituted to use as key
            for (var route of routerRoutes.slice(1)) {
                if (routeMatched.startsWith(route.path)) {
                    var fullpath = route.path
                    for (var kvpair of Object.entries(this.$route.params)) {
                        fullpath = fullpath.replace(':' + kvpair[0], kvpair[1])
                    }
                    this.crumbs.push({ route: fullpath, routeName: route.name, displayName: null })
                }
            }
        },
        // Load the displayname map from cache, complete crumbs from cache where possible, do aliasing
        addDisplayNames () {
            this.cachedMap = store.state.cachedMap

            for (var crumb of this.crumbs) {
                if (!this.settings.namedViews[crumb.routeName]) {
                    crumb.displayName = this.settings.aliases[crumb.routeName] || crumb.routeName
                } else {
                    crumb.displayName = this.cachedMap[crumb.route] || null
                }
            }
        },
        // If any are still missing display names (not in cache), request the names and set them in cache
        fillCache () {
            var crumbsMissingDisplayName = this.crumbs.filter(crumb => !crumb.displayName)

            // Incrementally build request
            var request = {}
            for (var crumb of crumbsMissingDisplayName) {
                var paramName = this.settings.namedViews[crumb.routeName].primaryParam
                request[paramName] = this.$route.params[paramName]
            }

            if (crumbsMissingDisplayName.length > 0) {
                commonAPI.get_names(request).then(data => {
                    for (var crumb of crumbsMissingDisplayName) {
                        crumb.displayName = data[this.settings.namedViews[crumb.routeName].apiReturnValue]
                        this.cachedMap[crumb.route] = crumb.displayName
                    }
                }).then(_ => {
                    store.setCachedMap(this.cachedMap)
                })
            }
        },
        eyeClick () {
            this.$emit('eye-click')
        },
        editClick () {
            this.$emit('edit-click')
        },
        canEdit () {
            var pageName = this.$route.name

            if ((pageName === 'Home' && this.$root.isAdmin()) ||
               (pageName === 'Course' && this.$root.canEditCourse()) ||
               (pageName === 'Assignment' && this.$root.canEditCourse())) {
                return true
            }
        }
    },
    created () {
        this.findRoutes()
        this.addDisplayNames()
        this.fillCache()
    }
}
</script>

<style lang="sass">
.breadcrumb-container
    padding-right: 10px
</style>