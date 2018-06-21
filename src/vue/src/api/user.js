import auth from '@/api/auth'

export default {
    /* Get own user data. */
    getOwnUserData () {
        return auth.authenticatedGet('/get_own_user_data/')
            .then(response => response.data.user)
    },

    /* Update user data. */
    updateUserData (username) {
        return auth.authenticatedPost('/update_user_data/', {username: username})
    },

    /* Update profile picture. */
    updateProfilePicture (file) {
        return auth.authenticatedFilePost('/update_user_data/', {picture: file})
    },

    /* Change whether the user gets grade notification or not.
     * if getsNotified is "true" the users gets notified by mail when a grade changes.
     * if getsNotified is "false" the users WONT  get notified by mail when a grade changes.
     * else nothing changes (invalid argument).
     */
    update_grade_notification (getsNotified) {
        return auth.authenticatedPost('/update_grade_notification/', {new_value: getsNotified}).then(r => r.data.new_value)
    },

    /* Change whether the user gets comment notification or not.
     * if getsNotified is "true" the users gets notified by mail when a there is a new comment.
     * if getsNotified is "false" the users WONT  get notified by mail when a there is a new comment.
     * else nothing changes (invalid argument).
     */
    update_comment_notification (getsNotified) {
        return auth.authenticatedPost('/update_comment_notification/', {new_value: getsNotified}).then(r => r.data.new_value)
    }
}