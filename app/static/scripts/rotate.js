$(window).on('load', function() {
    signIn = document.getElementById("sign-in-container")
    if (signIn) {
        setInterval(() => {
            signIn.style.setProperty('--grad', (parseInt(signIn.style.getPropertyValue("--grad")) + 2) % 360);
        }, 20);
    }
});