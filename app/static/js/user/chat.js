var socket;
$(document).ready(function () {    
    let path = window.location.pathname.split("/")

    let reciever = path.pop();
    let chat_link = path.pop()

    if (chat_link != "chat")
        return

    socket = io.connect("http://" + document.domain + ":" + location.port);

    socket.on("connect", function () {
        socket.emit("join", { reciever: reciever });
    });

    // scroll to the bottom
    let messagesDiv = $("#messages")
    messagesDiv.scrollTop(messagesDiv.prop("scrollHeight"));

    socket.on("message", function (msg) {
        json = JSON.parse(msg);

        messageLine = messageComponent(json.message, json.author);

        if (json.author == "server") {
            $(messageLine).addClass("server");
            messageLine.innerHTML = "   > " + messageLine.innerHTML;
        }
        $("#messages").append(messageLine);

        // scroll to the bottom
        $("#messages").animate ({
            scrollTop: $("#messages")[0].scrollHeight
        }, 60);;

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
