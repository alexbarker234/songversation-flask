var socket;
$(document).ready(function () {
    reciever = objectID = window.location.pathname.split("/").pop();

    socket = io.connect("http://" + document.domain + ":" + location.port);

    socket.on("connect", function () {
        socket.emit("join", { reciever: reciever });
    });

    socket.on("message", function (msg) {
        console.log(msg);
        json = JSON.parse(msg);

        messageLine = $($.parseHTML(`<div class="chat-line ${json.reciever == reciever ? "reciever" : "sender"}">${json.message}</div>`));

        if (json.author == "server") {
            $(messageLine).addClass("server");
            messageLine.innerHTML = "   > " + messageLine.innerHTML;
        }
        $("#messages").append(messageLine);

        console.log("recieved message");
    });

    $("#sendButton").on("click", function () {
        socket.send({ message: $("#myMessage").val(), reciever: reciever });
        $("#myMessage").val("");
    });
});

function leave_room() {
    socket.emit("left", {}, function () {
        socket.disconnect();
    });
}
