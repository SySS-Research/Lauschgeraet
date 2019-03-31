$(document).ready(function() {
    $('.ajax-switch').change(toggle_onoff);
});

function toggle_onoff() {
    $.ajax({
        url: '/toggleswitch',
        data: {"name":this.id},
        type: 'POST',
        success: flash_message,
    });
    if ( this.id == "onoffswitch" ) {
        // TODO verifiy status and set switch accordingly. it might have
        // failed
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
        success: flash_message,
    });
};

function flash_message(data){
    if (data) {
        var msg = $('<div>').html(data);
        $('#flash-msg').append(msg);
        $('#flash-msg .toast').toast("show");
    };
};

function update_mitm_rules(){
    $.get('/mitmtable', function(data) {
        $('#mitm-table').replaceWith(data);
        feather.replace();
    });
};

function ruleAdd() {
    var proto = $('#new-rule-proto').val();
    var olddest = $('#new-rule-olddest').val();
    var newdest = $('#new-rule-newdest').val();
    $.ajax({
        url: '/addrule',
        data: {
            "proto": proto,
            "olddest": olddest,
            "newdest": newdest,
        },
        type: 'POST',
        success: flash_message,
    });
    update_mitm_rules();
};

function ruleEdit() {
    var number = document.getElementById("new-rule-number").innerHTML;
    var proto = $('#new-rule-proto').val();
    var olddest = $('#new-rule-olddest').val();
    var newdest = $('#new-rule-newdest').val();
    $.ajax({
        url: '/editrule',
        data: {
            "number": number,
            "proto": proto,
            "olddest": olddest,
            "newdest": newdest,
        },
        type: 'POST',
        success: flash_message,
    });
    update_mitm_rules();
};


$(document).ready(function(){
	$('#add-iptables-rule').click(function(){
        $.get('/stub-newrule?add', function(data){
            $('#mitm-table > tbody:last-child').append(data);
            feather.replace();
        });
    });
});

function delete_mitm_rule(n){
    var line = $(`#rule-${n}`);
    $.ajax({
        url: '/deleterule',
        data: {
            "number": n,
        },
        type: 'POST',
        success: flash_message,
    });
    update_mitm_rules();
};

function edit_mitm_rule(n){
    var line = $(`#rule-${n}`);
    $.get(`/stub-editrule?n=${n}`, function(data) {
        line.replaceWith(data);
        feather.replace();
    });
};
