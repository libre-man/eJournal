import auth from '@/api/auth'

export default {
    /* Get data of a course specified with its ID. */
    get_course_data (cID) {
        return auth.authenticatedGet('/get_course_data/' + cID + '/')
            .then(response => response.data.course)
    },

    /* Get the courses where the logged in user is the teacher. */
    get_user_teacher_courses () {
        return auth.authenticatedGet('/get_user_teacher_courses/')
            .then(response => response.data.courses)
    },

    /* Get user courses.
     * Requests all the users courses.
     * returns a list of all courses.
     */
    get_user_courses () {
        return auth.authenticatedGet('/get_user_courses/')
            .then(response => response.data.courses)
    },

    get_users (cID) {
        return auth.authenticatedGet('/get_course_users/' + cID + '/')
            .then(response => response.data)
    },

    get_unenrolled_users (cID) {
        return auth.authenticatedGet('/get_unenrolled_users/' + cID + '/')
            .then(response => response.data.users)
    },

    /* Get upcomming deadlines. */
    get_upcoming_course_deadlines (cID) {
        return auth.authenticatedGet('/get_upcoming_course_deadlines/' + cID + '/')
            .then(response => response.data.deadlines)
    },

    /* Create a new course. */
    create_new_course (name, abbr, startdate, lti_id = null) {
        return auth.authenticatedPost('/create_new_course/', {
            name: name,
            abbr: abbr,
            startdate: startdate,
            lti_id: lti_id
        }).then(response => response.data)
    },

    /* Updates an existing course. */
    update_course (cID, name, abbr, startDate) {
        return auth.authenticatedPost('/update_course/', {
            cID: cID,
            name: name,
            abbr: abbr,
            startDate: startDate
        }).then(response => response.data.course)
    },

    /* Connect an existing course to lti course. */
    connect_course_lti (cID, ltiID) {
        return auth.authenticatedPost('/connect_course_lti/', {
            cID: cID,
            lti_id: ltiID
        }).then(response => response.data.course)
    },

    /* Updates the role of a student linked to a course. */
    update_course_with_studentID (uID, cID) {
        return auth.authenticatedPost('/update_course_with_studentID/', {
            uID: uID,
            cID: cID
        }).then(response => response.data.result)
    },

    /* Deletes an existing course. */
    delete_course (cID) {
        return auth.authenticatedPost('/delete_course/', {
            cID: cID
        }).then(response => response.message)
    },

    /* Updates the role of a student linked to a course. */
    update_user_role_course (uID, cID, role) {
        return auth.authenticatedPost('/update_user_role_course/', {
            uID: uID,
            cID: cID,
            role: role
        }).then(response => response.data.result)
    },

    /* Updates the role of a student linked to a course. */
    delete_user_from_course (uID, cID) {
        return auth.authenticatedPost('/delete_user_from_course/', {
            uID: uID,
            cID: cID
        }).then(response => response.data.result)
    }
}
