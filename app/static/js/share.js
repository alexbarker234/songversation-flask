// Check if the Web Share API is supported by the browser
// disabled for now - TODO: reimplement in the finish screen
/*document.addEventListener("DOMContentLoaded", function () {
    if (navigator.share) {
        // Add a click event listener to the share button
        var shareButton = document.getElementById("shareButton");
        shareButton.addEventListener("click", function () {
            // Call the share() method of the Web Share API
            navigator
                .share({
                    title: "Songversation",
                    text: "Check out this page!",
                    url: "#",
                    icon: "app/static/favicon.ico",
                })
                .then(function () {
                    console.log("Sharing succeeded.");
                })
                .catch(function (error) {
                    console.error("Sharing failed:", error);
                });
        });
    }
});
*/