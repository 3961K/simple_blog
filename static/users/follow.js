function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(function() {
    $(".btn.btn-info").on("click", function(e) {
        e.preventDefault();
        const csrfToken = getCookie("csrftoken");
        const follower = $("input[name='follower']").val();
        const url = $(this).parents("form").attr("action");
        const status_text = $.ajax({
            url: url,
            type: "POST",
            data: {
                'follower': follower,
            },
            async: false,
            dataType: "json",
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            },
        }).responseText;

        const status = (JSON.parse(status_text))["data"]["status"];
        if (status == "follow") {
            $(this).val("フォロー中");
        } else if (status  == "notfollow") {
            $(this).val("フォローする");
        }
    });
});
