$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:5000');

    socket.on('connect', function() {
        socket.send("connection bagawaga")
    });

    socket.on('message', function(msg) {
        source = msg.substr(0, msg.indexOf(" ") - 1)
        msg = msg.substr(msg.indexOf(" ") + 1);

        messageLine = document.createElement('div');
        console.log(source);
        messageLine.innerHTML = msg;
        $(messageLine).addClass('chat-line')
        if (source == 'server'){
            $(messageLine).addClass('server')
            messageLine.innerHTML = "   > " + messageLine.innerHTML;
        }


        $("#messages").append(messageLine)
        $("#messages").animate ({
                scrollTop: $("#messages")[0].scrollHeight
            }, 60);;
        console.log($("#messages").scrollTop, $("#messages")[0].scrollHeight);
        //$("#messages").scrollTop($("#messages")[0].scrollHeight)
        console.log("recieved message");
    });

    $('#sendButton').on('click', function() {
        console.log('click')
        socket.send($('#myMessage').val());
        $('#myMessage').val('');
    });
});