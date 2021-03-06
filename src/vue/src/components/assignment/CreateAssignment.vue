<template>
    <b-card class="no-hover">
        <!-- TODO: Create default formats. -->
        <b-form @submit.prevent="onSubmit" @reset.prevent="onReset">
            <h2 class="field-heading">Assignment Name</h2>
            <b-input class="multi-form theme-input"
                v-model="form.assignmentName"
                placeholder="Assignment name"
                required
            />
            <h2 class="field-heading">Description</h2>
            <text-editor class="multi-form"
                :id="'text-editor-assignment-description'"
                :givenContent="'Description of the assignment'"
                @content-update="form.assignmentDescription = $event"
                :footer="false"
            />
            <h2 class="field-heading">Points possible</h2>
            <b-input class="multi-form theme-input"
            v-model="form.pointsPossible"
            placeholder="Points"
            type="number"/>
            <b-row>
                <b-col xl="4">
                    <h2 class="field-heading">Unlock date</h2>
                    <b-input class="multi-form theme-input"
                    :value="form.unlockDate && form.unlockDate.replace(' ', 'T')"
                    @input="form.unlockDate = $event && $event.replace('T', ' ')"
                    type="datetime-local"/>
                </b-col>
                <b-col xl="4">
                    <h2 class="field-heading">Due date</h2>
                    <b-input class="multi-form theme-input"
                    :value="form.dueDate && form.dueDate.replace(' ', 'T')"
                    @input="form.dueDate = $event && $event.replace('T', ' ')"
                    type="datetime-local"/>
                </b-col>
                <b-col xl="4">
                    <h2 class="field-heading">Lock date</h2>
                    <b-input class="multi-form theme-input"
                    :value="form.lockDate && form.lockDate.replace(' ', 'T')"
                    @input="form.lockDate = $event && $event.replace('T', ' ')"
                    type="datetime-local"/>
                </b-col>
            </b-row>
            <b-button class="float-left change-button mt-2" type="reset">
                <icon name="undo"/>
                Reset
            </b-button>
            <b-button class="float-right add-button mt-2" type="submit">
                <icon name="plus-square"/>
                Create
            </b-button>
        </b-form>
    </b-card>
</template>

<script>
import textEditor from '@/components/assets/TextEditor.vue'
import icon from 'vue-awesome/components/Icon'

import assignmentAPI from '@/api/assignment'

export default {
    name: 'CreateAssignment',
    props: ['lti', 'page'],
    data () {
        return {
            form: {
                assignmentName: '',
                assignmentDescription: '',
                courseID: '',
                ltiAssignID: null,
                pointsPossible: null,
                unlockDate: null,
                dueDate: null,
                lockDate: null
            }
        }
    },
    components: {
        'text-editor': textEditor,
        icon
    },
    methods: {
        onSubmit () {
            assignmentAPI.create({
                name: this.form.assignmentName,
                description: this.form.assignmentDescription,
                course_id: this.form.courseID,
                lti_id: this.form.ltiAssignID,
                points_possible: this.form.pointsPossible,
                unlock_date: this.form.unlockDate,
                due_date: this.form.dueDate,
                lock_date: this.form.lockDate
            })
                .then(assignment => {
                    this.$emit('handleAction', assignment.id)
                    this.onReset(undefined)
                    this.$store.dispatch('user/populateStore').catch(_ => {
                        this.$toasted.error('The website might be out of sync, please login again.')
                    })
                })
                .catch(error => { this.$toasted.error(error.response.data.description) })
        },
        onReset (evt) {
            if (evt !== undefined) {
                evt.preventDefault()
            }
            /* Reset our form values */
            this.form.assignmentName = ''
            this.form.assignmentDescription = ''
            this.form.unlockDate = undefined
            this.form.dueDate = undefined
            this.form.lockDate = undefined

            /* Trick to reset/clear native browser form validation state */
            this.show = false
            this.$nextTick(() => { this.show = true })
        }
    },
    mounted () {
        if (this.lti !== undefined) {
            this.form.assignmentName = this.lti.ltiAssignName
            this.form.ltiAssignID = this.lti.ltiAssignID
            this.form.pointsPossible = this.lti.ltiPointsPossible
            this.form.unlockDate = this.lti.ltiAssignUnlock.slice(0, -9)
            this.form.dueDate = this.lti.ltiAssignDue.slice(0, -9)
            this.form.lockDate = this.lti.ltiAssignLock.slice(0, -9)
            this.form.courseID = this.page.cID
        } else {
            this.form.courseID = this.$route.params.cID
        }
    }
}
</script>
