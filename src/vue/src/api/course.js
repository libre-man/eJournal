import auth from '@/api/auth'

export default {
    /* Get user courses.
     * Requests all the users courses.
     * returns a list of all courses.
     */
    get_user_courses () {
        return auth.authenticatedGet('/get_user_courses/')
            .then(response => response.data.courses)
    }
}