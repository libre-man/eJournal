<!--
    Loads a filled in template of an entry and the corresponding
    comments. The teacher tools will also be loaded if the user has the
    right permissions.
-->
<template>
    <div v-if="entryNode.entry !== null">
        <b-card class="entry-card no-hover entry-card-teacher" :class="$root.getBorderClass($route.params.cID)">
            <div v-if="$hasPermission('can_grade')" class="grade-section shadow sticky">
                <b-form-input class="theme-input" step="0.01" size="2" v-model="grade" autofocus placeholder="0" min="0.0"></b-form-input>
                <b-form-checkbox v-model="published" value=true unchecked-value=false data-toggle="tooltip" title="Show grade to student">
                    Published
                </b-form-checkbox>
                <b-button class="add-button" @click="commitGrade">
                    <icon name="save" scale="1"/>
                    Save grade
                </b-button>
            </div>
            <div v-else class="grade-section shadow">
                <span v-if="tempNode.entry.published">
                    {{ entryNode.entry.grade }}
                </span>
                <span v-else>
                    <icon name="hourglass-half"/>
                </span>
            </div>

            <h2 class="mb-2">{{ entryNode.entry.template.name }}</h2>
            <entry-fields
                :nodeID="entryNode.nID"
                :template="entryNode.entry.template"
                :completeContent="completeContent"
                :displayMode="true"
                :authorUID="$parent.journal.student.id"
            />
        </b-card>

        <comment-card :eID="entryNode.entry.id" :entryGradePublished="entryNode.entry.published"/>
    </div>
    <b-card v-else class="no-hover" :class="$root.getBorderClass($route.params.cID)">
        <h2 class="mb-2">{{entryNode.template.name}}</h2>
        <b>No submission for this student</b>
    </b-card>
</template>

<script>
import commentCard from '@/components/journal/CommentCard.vue'
import entryFields from '@/components/entry/EntryFields.vue'
import entryAPI from '@/api/entry'
import icon from 'vue-awesome/components/Icon'

export default {
    props: ['entryNode'],
    data () {
        return {
            tempNode: this.entryNode,
            completeContent: [],
            grade: null,
            published: null
        }
    },
    watch: {
        entryNode () {
            this.completeContent = []
            this.setContent()
            this.tempNode = this.entryNode

            if (this.entryNode.entry !== null) {
                this.grade = this.entryNode.entry.grade
                this.published = this.entryNode.entry.published
            } else {
                this.grade = null
                this.published = true
            }
        }
    },
    created () {
        this.setContent()

        if (this.entryNode.entry) {
            this.grade = this.entryNode.entry.grade
            this.published = this.entryNode.entry.published
        }
    },
    methods: {
        setContent () {
            /* Loads in the data of an entry in the right order by matching
             * the different data-fields with the corresponding template-IDs. */
            var checkFound = false

            if (this.entryNode.entry !== null) {
                for (var templateField of this.entryNode.entry.template.field_set) {
                    checkFound = false

                    for (var content of this.entryNode.entry.content) {
                        if (content.field === templateField.id) {
                            this.completeContent.push({
                                data: content.data,
                                id: content.field
                            })

                            checkFound = true
                            break
                        }
                    }

                    if (!checkFound) {
                        this.completeContent.push({
                            data: null,
                            id: templateField.id
                        })
                    }
                }
            }
        },
        commitGrade () {
            if (this.grade !== null) {
                this.tempNode.entry.grade = this.grade
                this.tempNode.entry.published = (this.published === 'true' || this.published === true)

                if (this.published === 'true' || this.published === true) {
                    entryAPI.update(this.entryNode.entry.id, {grade: this.grade, published: 1})
                        .then(_ => {
                            this.$toasted.success('Grade updated and published.')
                            this.$emit('check-grade')
                        })
                        .catch(error => { this.$toasted.error(error.response.data.description) })
                } else {
                    entryAPI.update(this.entryNode.entry.id, {grade: this.grade, published: 0})
                        .then(_ => {
                            this.$toasted.success('Grade updated but not published.')
                            this.$emit('check-grade')
                        })
                        .catch(error => { this.$toasted.error(error.response.data.description) })
                }
            }
        }
    },
    components: {
        'comment-card': commentCard,
        'entry-fields': entryFields,
        icon
    }
}
</script>
<style lang="sass">
@import '~sass/modules/colors.sass'
.timestamp
    float: right
    font-family: 'Roboto Condensed', sans-serif
    color: grey
    svg
        fill: grey

hr
    width: 120%
    margin-left: -10px !important
    border-color: $theme-dark-grey
    margin: 30px 0px 5px 0px
</style>
