$(document).ready(function() {
  $('.ajax-switch').change(toggle_onoff);
});

function toggle_onoff() {
  $.ajax({
    url: '/toggleswitch',
    data: {"name":this.id},
    type: 'POST',
  });
}

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

function ruleAdd() {
    var proto = $('#new-rule-proto').val();
    var port = $('#new-rule-port').val();
    var olddest = $('#new-rule-olddest').val();
    var newdest = $('#new-rule-newdest').val();
    $.ajax({
        url: '/addrule',
        data: {
            "proto": proto,
            "port": port,
            "olddest": olddest,
            "newdest": newdest,
        },
        type: 'POST',
    });
    location.reload();
};

function ruleEdit() {
    var number = document.getElementById("new-rule-number").innerHTML;
    var proto = $('#new-rule-proto').val();
    var port = $('#new-rule-port').val();
    var olddest = $('#new-rule-olddest').val();
    var newdest = $('#new-rule-newdest').val();
    $.ajax({
        url: '/editrule',
        data: {
            "number": number,
            "proto": proto,
            "port": port,
            "olddest": olddest,
            "newdest": newdest,
        },
        type: 'POST',
    });
    location.reload();
};

function ruleAbort() {
    $('#iptables-table > tbody > tr:last-child').remove();
};

function ruleAbortEdit(n) {
    // $(`#rule-${n}`).remove();
    location.reload();
};

$(document).ready(function(){
	$('#add-iptables-rule').click(function(){
        $.get('/stub-newrule?add', function(data){
            $('#iptables-table > tbody:last-child').append(data);
            feather.replace();
        });
    });
});

$(document).ready(function(){
	$('.delete-iptables-rule').click(function(){
        var line = $(this).closest('tr');
        n = line.children().first().text();
        $.ajax({
            url: '/deleterule',
            data: {
                "number": n,
            },
            type: 'POST',
        });
        location.reload();
    });
});



$(document).ready(function(){
	$('.edit-iptables-rule').click(function(){
        var line = $(this).closest('tr');
        n = line.children().first().text();
        $.get(`/stub-editrule?n=${n}`, function(data) {
            line.replaceWith(data);
            feather.replace();
        });
    });
});


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
            socket.emit('comando', {msg: text});
        }
    });
});
function leave_room() {
    socket.disconnect();
    window.location.href = "http://www.google.com";
}
