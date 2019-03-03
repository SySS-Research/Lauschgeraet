var socket;
$(document).ready(function(){
    socket = io.connect('http://' + document.domain + ':' + location.port + '/shell_socket');
    socket.on('connect', function() {
        socket.emit('joined', {});
    });
    socket.on('message', function(data) {
        $('#shell').val($('#shell').val() + data.msg);
        $('#shell').scrollTop($('#shell')[0].scrollHeight);
    });
    socket.on('status', function(data) {
        $('#shell').val($('#shell').val() + '<' + data.msg + '>\n');
        $('#shell').scrollTop($('#shell')[0].scrollHeight);
    });
    $('#text').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#text').val();
            $('#text').val('');
            socket.emit('command', {msg: text});
        }
    });
});
