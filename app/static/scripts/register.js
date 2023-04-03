$(window).on('load', function() {
    username = document.getElementById("username");
    firstPass = document.getElementById("first-pass");
    repeatPass = document.getElementById("repeat-pass");

    // check if passwords match
    if (firstPass && repeatPass){
        firstPass.addEventListener("keyup", (e) => {
            checkMatchingPass(firstPass, repeatPass);
        })
        repeatPass.addEventListener("keyup", (e) => {
            checkMatchingPass(firstPass, repeatPass);
        })
    }
    if (username) {
        // check if username is taken 1 second after stopping typing
        let usernameCheckTimout;
        username.addEventListener("keyup", (e) => {
            clearTimeout(usernameCheckTimout);
            usernameCheckTimout = setTimeout(() => {
                checkUsernameFree(username.value)
            }, 1000);
        });
        // or on page load
        checkUsernameFree(username.value)
    }
});

function checkUsernameFree(username){
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

function markUsername(free){
    info = document.getElementById("username-info");
    text = document.getElementById("username-info-text");
    icon = document.getElementById("username-info-icon");
    if (info){
        if (free) {
            text.innerHTML = "all good";
            icon.className = "glyphicon glyphicon-question-sign";
            info.classList.remove("error-text");
        }
        else {
            text.innerHTML = "Sorry, that username is taken";
            icon.className = "glyphicon glyphicon-exclamation-sign";
            info.classList.add("error-text");
        }
    }
}

function checkMatchingPass(firstPass, repeatPass) {
    if (firstPass.value != repeatPass.value){
        if (!repeatPass.classList.contains("incorrect")) {
            repeatPass.classList.add("incorrect");
        }
    }
    else {
        repeatPass.classList.remove("incorrect");
    }
}