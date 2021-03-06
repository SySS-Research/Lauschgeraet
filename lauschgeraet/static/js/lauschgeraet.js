$(document).ready(function() {
    $.get('/state', function(data) {
        $('#lg-status').replaceWith(data);
        $('.ajax-switch').change(toggle_onoff);
        feather.replace();
    });
    $('.ajax-switch').change(toggle_onoff);
});

function toggle_onoff() {
    $.ajax({
        url: '/toggleswitch',
        data: {"name":this.id},
        type: 'POST',
        success: toggle_onoff_callback,
    });
    // replace with waiting indicator, a spinner or someting
}

function toggle_onoff_callback(response) {
    $.get('/state', function(data) {
        $('#lg-status').replaceWith(data);
        $('.ajax-switch').change(toggle_onoff);
        feather.replace();
    });
    flash_message(response);
};

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

function startservice(n) {
    $.ajax({
        url: '/startservice',
        data: {
            "n": n,
        },
        type: 'POST',
        success: function() { location.reload(); }
    });
};

function stopservice(n) {
    $.ajax({
        url: '/stopservice',
        data: {
            "n": n,
        },
        type: 'POST',
        success: function() { location.reload(); }
    });
};

$("#service-output-modal").on("show.bs.modal", function(e) {
    var link = $(e.relatedTarget).attr("href");
    $(this).find(".modal-body").attr('data-href', link);
    $(this).find(".modal-body").load(link);
});



// this is for installing or updating services
$(".service-form .btn-group .btn").click(function(){
    var n = $(this).closest('.service-form').attr('data-n');
    var action = $(this).attr('data-action');
    // TODO insert spinner
    var data = {
        "n": n,
        "action": action,
    };
    if (action == 'updateargs') {
        $(".service-json-field").each(function(){
            data[$(this).attr("data-field")] =  $(this).attr("value");
        });
    };
    $.ajax({
        url: '/service',
        type: 'POST',
        data: data,
        success: function() { location.reload(); }
    });
});

$('#service-output-modal .service-reload').click(function(){
    var objDiv = $(this).closest(".modal-content").find(".modal-body");
    var link = objDiv.attr('data-href');
    $(this).find(".modal-body").load(link);
});

$('#service-output-modal .service-scroll-down').click(function(){
    var objDiv = $(this).closest(".modal-content").find(".modal-body");
    objDiv.scrollTop(objDiv[0].scrollHeight);
});
