<template>
    <content-single-table-column>
        <bread-crumb>&nbsp;</bread-crumb>
        <b-card class="settings-card mb-4 no-hover">
            <b-button @click="reset()" class="multi-form change-button">
                <icon name="undo"/>
                Undo Changes
            </b-button>
            <b-button @click="update()" class=" float-right multi-form add-button">
                <icon name="save"/>
                Save
            </b-button>
        </b-card>
        <div class="table-responsive">
            <table class="table table-bordered table-hover">
                <thead>
                    <tr>
                        <th/>
                        <th v-for="role in roles" :key="'th-' + role">
                            <b-button v-if="!undeleteableRoles.includes(role)" @click="deleteRole(role)" class="delete-button">
                                {{ role }}
                                <icon name="trash"/>
                            </b-button>
                            <span v-else>
                                {{ role }}
                            </span>
                        </th>
                        <th>
                            <b-button @click="modalShow = !modalShow" class="add-button">
                                <icon name="plus-square"/>
                                Add Role
                            </b-button>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="permission in permissions" :key="permission">
                        <td class="permission-column">{{ formatPermissionString(permission) }}</td>
                        <td v-for="role in roles" :key="role + '-' + permission">
                            <custom-checkbox
                                :class="{ 'input-disabled': essentialPermission(role, permission) }"
                                @checkbox-toggle="updateRole"
                                :role="role"
                                :permission="permission"
                                :receivedState="setState(role, permission)"/>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <b-modal
            @shown="focusRoleNameInput"
            title="New Role"
            size="lg"
            v-model="modalShow"
            hide-footer>
            <b-card class="no-hover">
                <b-form-input
                    @keyup.enter.native="addRole"
                    v-model="newRole"
                    class="multi-form theme-input"
                    ref="roleNameInput"
                    required placeholder="Role name"/>
                <b-button @click="modalShow = false" class="delete-button float-left">
                    <icon name="ban"/>
                    Cancel
                </b-button>
                <b-button @click="addRole" class="add-button float-right">
                    <icon name="user-plus"/>
                    Create new role
                </b-button>
            </b-card>
        </b-modal>
    </content-single-table-column>
</template>

<script>
import breadCrumb from '@/components/assets/BreadCrumb.vue'
import contentSingleTableColumn from '@/components/columns/ContentSingleTableColumn.vue'
import customCheckbox from '@/components/assets/CustomCheckbox.vue'
import icon from 'vue-awesome/components/Icon'
import roleAPI from '@/api/role'
import commonAPI from '@/api/common'

export default {
    name: 'UserRoleConfiguration',
    props: {
        cID: {
            required: true
        }
    },
    data () {
        return {
            roles: [],
            permissions: [],
            backupPermissions: [],
            roleConfig: [],
            originalRoleConfig: [],
            defaultRoles: [],
            selectRoles: [
                {value: null, text: 'Please select a role'},
                {value: 'Student', text: 'Student'},
                {value: 'TA', text: 'TA'},
                {}
            ],
            undeleteableRoles: ['Student', 'TA', 'Teacher'],
            selectedRole: null,
            modalShow: false,
            newRole: '',
            essentialPermissions: {'Teacher': ['can_edit_course_roles']}
        }
    },
    methods: {
        essentialPermission (role, permission) {
            return this.essentialPermissions[role] && this.essentialPermissions[role].includes(permission)
        },
        updateRole (list) {
            var role = list[0]
            var permission = list[1]
            var state = list[2]

            var i = this.roleConfig.findIndex(p => p.name === role)

            this.roleConfig[i][permission] = (state ? 1 : 0)
        },
        callocRoleObject (role) {
            /* Initialises a role object with the given name, the pages cID
             * and permissions object with all  corresponding permissions set to false. */
            var newPermissions = {}

            for (var i = 0; i < this.permissions.length; i++) {
                newPermissions[this.permissions[i]] = 0
            }

            return { name: role, cID: this.cID, permissions: newPermissions }
        },
        deepCopyRoles (roles) {
            var deepCopy = []

            for (var i = 0; i < roles.length; i++) {
                deepCopy.push({ name: roles[i].name, id: roles[i].id })

                for (var j = 0; j < this.permissions.length; j++) {
                    deepCopy[i][this.permissions[j]] = roles[i][this.permissions[j]]
                }
            }

            return deepCopy
        },
        addRole () {
            /* Adds a new role, clearing the input buffer and updating the
             * roles list and roleconfiguration objects. */
            this.roleConfig.push(this.callocRoleObject(this.newRole))
            this.roles.push(this.newRole)

            this.modalShow = false
            this.newRole = ''
        },
        focusRoleNameInput () {
            /* Ensures the modal name field is focused upon the modal opening. */
            this.$refs.roleNameInput.focus()
        },
        setState (role, permission) {
            var correctRole = (this.roleConfig.filter(arg => { return arg.name === role }))[0]
            if (correctRole !== undefined) {
                return correctRole[permission] === true
            }

            return false
        },
        // TODO: Undo changes button doesnt work
        reset () {
            /* Resets the configuration to the defaults by deep copies.
             * Forces reupdate of custom checkbox components,
             * by temporarily clearing the roles and permissions lists.
             * This could be prevented by creating a custom data model which
             * could interact with v-model.
             * However scaling should not be a problem here (time choice to keep
             * working with the databse given format.)  */
            if (confirm('This will undo all unsaved changes\n Are you sure you want to continue?')) {
                this.roleConfig = this.deepCopyRoles(this.originalRoleConfig)

                this.roles = []
                this.backupPermissions = Array.from(this.permissions)
                this.permissions = []
                this.$nextTick(() => {
                    this.roles = Array.from(this.defaultRoles)
                    this.permissions = this.backupPermissions
                })
            }
        },
        update () {
            roleAPI.update(this.cID, this.roleConfig)
                .then(_ => {
                    this.originalRoleConfig = this.deepCopyRoles(this.roleConfig)
                    this.defaultRoles = Array.from(this.roles)
                    this.$toasted.success('Course roles succesfully updated.')
                    this.checkPermission()
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        formatPermissionString (str) {
            /* Converts underscores to spaces and capatilises the first letter. */
            var temp = str.split('_').join(' ')
            return temp[0].toUpperCase() + temp.slice(1)
        },
        deleteRole (role) {
            if (confirm('Are you sure you want to delete the role "' + role + '" from this course?')) {
                if (this.defaultRoles.includes(role)) {
                    /* handle server update. */
                    roleAPI.delete(this.cID, role)
                        .then(_ => {
                            this.deleteRoleLocalConfig(role)
                            this.deleteRoleServerLoadedConfig(role)
                            this.$toasted.success('Role deleted succesfully!')
                        })
                        .catch(error => this.$toasted.error(error.response.data.description))
                } else {
                    this.deleteRoleLocalConfig(role)
                }
            }
        },
        deleteRoleLocalConfig (role) {
            var i = this.roleConfig.findIndex(p => p.name === role)
            this.roleConfig.splice(i, 1)
            i = this.roles.findIndex(p => p === role)
            this.roles.splice(i, 1)
        },
        deleteRoleServerLoadedConfig (role) {
            var i = this.originalRoleConfig.findIndex(p => p.name === role)
            this.originalRoleConfig.splice(i, 1)
            i = this.defaultRoles.findIndex(p => p === role)
            this.defaultRoles.splice(i, 1)
        },
        checkPermission () {
            commonAPI.getPermissions(this.cID)
                .then(coursePermissions => {
                    this.$store.commit('user/UPDATE_PERMISSIONS', { permissions: coursePermissions, key: 'course' + this.cID })
                    if (!this.$hasPermission('can_edit_course_roles')) { this.$router.push({ name: 'Home' }) }
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        checkChanged () {
            for (var i = 0; i < this.roleConfig.length; i++) {
                for (var j = 0; j < this.permissions.length; j++) {
                    if (this.roleConfig[i][this.permissions[j]] !== this.originalRoleConfig[i][this.permissions[j]]) {
                        return true
                    }
                }
            }

            return false
        }
    },
    created () {
        /* Initialises roles, permissions and role config as well as their defaults.
         * Roles and Permissions objects need to exist as deepcopy depends on then. */
        roleAPI.getFromCourse(this.cID)
            .then(roleConfig => {
                this.roleConfig = roleConfig

                roleConfig.forEach(role => {
                    this.defaultRoles.push(role.name)
                    this.roles.push(role.name)
                })
                this.permissions = Object.keys(roleConfig[0])
                this.permissions.splice(this.permissions.indexOf('id'), 1)
                this.permissions.splice(this.permissions.indexOf('name'), 1)
                this.permissions.splice(this.permissions.indexOf('course'), 1)

                this.originalRoleConfig = this.deepCopyRoles(roleConfig)
            })
            .catch(error => { this.$toasted.error(error.response.data.description) })
    },
    components: {
        'content-single-table-column': contentSingleTableColumn,
        'bread-crumb': breadCrumb,
        'custom-checkbox': customCheckbox,
        icon
    },
    beforeRouteLeave (to, from, next) {
        if (this.checkChanged() && !confirm('Unsaved changes will be lost if you leave. Do you wish to continue?')) {
            next(false)
            return
        }

        next()
    }
}
</script>

<style lang="sass">
.select-center
    text-align: center

.table th
    text-align: center

.table td
    text-align: center
    align-items: center

.permission-column
    text-align: left !important
</style>
