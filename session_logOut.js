// sesson loged our scenarios
{% if request.session.confirm_logout %}
<script>
    window.onload = function() {
    Swal.fire({
        title: 'Session Conflict!',
        text: "{{ request.session.alert_message|escapejs }}",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Ok',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            // ✅ User clicked Logout
            fetch("{% url 'confirm_logout_old_session' %}", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                localStorage.setItem('session_killed_after_lgout', Date.now().toString());  // Unique value everytime
                window.location.href = "{% url 'logout_confirmation_view' %}"; 
                
            });
        } else {
            // ❌ User clicked Stay
            fetch("{% url 'cancel_logout_alert' %}", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                console.log('User chose to stay logged in.');
                    window.location.href = "/logout/";  // This will log the user out in the current tab

            });
        }
    });
}
</script>
{% endif %}
