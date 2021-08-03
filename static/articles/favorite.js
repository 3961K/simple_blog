function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
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
    $('#favorite_button').on('click', function(e) {
        e.preventDefault();
        const csrfToken = getCookie('csrftoken');
        const username = document.forms["favorite"];
        const url = $(this).parents('form').attr('action');
        $.ajax({
            url: url,
            type: 'POST',
            data: $(username).serialize(),
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
        .done (function(data) {
            const status = data["data"]["status"];
            if (status == "favorited")
            {
                $("#favorite_button").attr("value", "お気に入り済み");
            }
            else if (status == "notfavorited")
            {
                $("#favorite_button").attr("value", "お気に入りに追加");
            }
        });
    });
});
