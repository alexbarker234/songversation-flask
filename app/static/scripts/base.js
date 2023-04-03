$(window).on('load', function() {
    
})
function loadProfilePic() {
    $.ajax({
        type : "POST",
        url : '/check_username',
        dataType: "json",
        data: JSON.stringify({'username':username}),
        contentType: 'application/json;charset=UTF-8',
        success: function (data) {
                markUsername(data == 0)
            }
        });
}