<!--TODO Check teacher permission;
    TODO Display student cards of those enrolled
    TODO Add deck of work to be checked for this assignment -->

<template>
    <content-columns>
        <bread-crumb @eye-click="customisePage" :currentPage="$route.params.assignmentName" :course="$route.params.courseName" slot="main-content-column"></bread-crumb>
        <div v-for="journal in assignmentJournals" :key="journal.uid" slot="main-content-column">
            <b-link tag="b-button" :to="{ name: 'Journal',
                                          params: {
                                              course: $route.params.course,
                                              assign: $route.params.assign,
                                              student: 'Rick',
                                              color: $route.params.color,
                                              courseName: $route.params.courseName,
                                              assignmentName: $route.params.assignmentName,
                                              journalName: journal.student
                                          }
                                        }">
                <student-card
                    :student="journal.student.name"
                    :studentNumber="journal.student.uID"
                    :studentPortraitPath="journal.student.picture"
                    :progress="journal.progress"
                    :entriesStats="journal.entriesStats">
                </student-card>
            </b-link>
        </div>
    </content-columns>
</template>

<script>
import contentColumns from '@/components/ContentColumns.vue'
import studentCard from '@/components/StudentCard.vue'
import breadCrumb from '@/components/BreadCrumb.vue'
import journal from '@/api/journal.js'

export default {
    name: 'Assignment',
    data () {
        return {
            assignmentJournals: []
        }
    },
    components: {
        'content-columns': contentColumns,
        'student-card': studentCard,
        'bread-crumb': breadCrumb
    },
    created () {
        journal.get_assignment_journals(this.$route.params.assign)
            .then(response => { this.assignmentJournals = response })
            .catch(_ => alert('Error while loading jounals'))
    },
    methods: {
        customisePage () {
            alert('Wishlist: Customise page')
        }
    }
}
</script>