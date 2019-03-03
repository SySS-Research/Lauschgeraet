$(document).ready(function() {
    $('.ajax-switch').change(toggle_onoff);
});

function toggle_onoff() {
    $.ajax({
        url: '/toggleswitch',
        data: {"name":this.id},
        type: 'POST',
    });
    if ( this.id == "onoffswitch" ) {
        $('#lg-mode-li').toggleClass('disabled');
        $('#lg-mode-a').toggleClass('disabled');
    };
}

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

function setMode(mode) {
    $.ajax({
        url: '/setmode',
        data: {"mode": mode},
        type: 'POST',
    });
};

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
