<template>
    <b-card :class="$root.colors[uID % $root.colors.length]" class="no-hover">
        <b-row>
            <b-col cols="4" sm="2">
                <img class="img-fluid" :src="portraitPath">
            </b-col>
            <b-col cols="8" order-sm="3" sm="4">
                 <b-form-select v-if="this.$root.canEditCourseRoles"
                                v-model="selectedRole"
                                class="mb-3"
                                :select-size="1">
                    <option v-for="r in roles" :key="r.name" :value="r.name">
                        {{r.name}}
                    </option>
                 </b-form-select>
                <b-button v-if="this.$root.canEditCourse"
                          @click.prevent.stop="removeFromCourse()"
                          class="delete-button full-width">
                    Remove
                </b-button>
            </b-col>
            <b-col cols="12" order-sm="2" sm="6">
                Name: {{ name }} <br/>
                Username: {{ studentNumber }} <br />
                Role: {{selectedRole}}
            </b-col>
        </b-row>
    </b-card>
</template>

<script>
import courseApi from '@/api/course.js'
import permissions from '@/api/permissions.js'

export default {
    props: {
        cID: {
            required: true
        },
        uID: {
            required: true
        },
        index: {
            required: true
        },
        studentNumber: {
            required: true
        },
        name: {
            required: true
        },
        portraitPath: {
            required: true
        },
        role: {
            required: true
        }
    },
    data () {
        return {
            selectedRole: '',
            init: true,
            roles: []
        }
    },
    methods: {
        removeFromCourse () {
            if (confirm('Are you sure you want to remove ' + name + '?')) {
                courseApi.delete_user_from_course(this.uID, this.cID)
                    .then(response => {
                        this.$emit('delete-participant', this.role,
                            this.name,
                            this.portraitPath,
                            this.uID)
                    })
                    .catch(_ => this.$toasted.error('Error while deleting user from course'))
            }
        }
    },
    watch: {
        selectedRole: function (val) {
            if (this.init) {
                this.init = false
            } else {
                this.selectedRole = val
                courseApi.update_user_role_course(
                    this.uID,
                    this.cID,
                    this.selectedRole)
                    .then(response => {})
            }
        }
    },
    created () {
        this.selectedRole = this.role

        permissions.get_course_roles(this.cID)
            .then(response => {
                this.roles = response
            })
    }
}
</script>