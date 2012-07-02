var table = [
    { "sp": "sprite-none",  "msg": "awaiting response" },
    { "sp": "sprite-yes",   "msg": "Yes" },
    { "sp": "sprite-maybe", "msg": "Not sure" },
    { "sp": "sprite-no",    "msg": "No" },
];

var logger;

function get_val(div)
{
    var val;

    try {
        val = parseInt(div.childNodes[0].value);
    } catch(err) {
        val = 0;
        div.childNodes[0].value = "" + val;
    }

    if (val >= table.length)
        val = 0;

    return val;
}

function set_div(div, val)
{
    var tm;
    try {
        tm = div.childNodes[1].value;
    } catch (e) {
        tm = "";
    }

    if (tm.length > 0)
        div.title = table[val]["msg"] + " - " + tm;
    else
        div.title = table[val]["msg"];
    div.className = "player sprites " + table[val]["sp"];
}

function init_div(div)
{
    set_div(div, get_val(div));
}

function change_state(div)
{
    var val;
    var reg;
    var match;
    var url;
    var json;
    var gmid;

    val = get_val(div);

    if (val == table.length - 1)
        val = 0;
    else
        val += 1;

    if (val == 0)
        val = 1;

    gmid = parseInt(/status(\d+)/.exec(div.id)[1]);

    json = { "val": val, "id": gmid };

    $.post(window.location.pathname, json,
           function(data) {
               var resp = jQuery.parseJSON(data);
               div.childNodes[0].value = val;
               if (resp.status != 0) {
                   $("#error")[0].innerHTML = "error " + resp.status + resp.ctx;
               } else {
                   div.childNodes[1].value = resp.since;
                   $("#error")[0].innerHTML = "";
               }
               set_div(div, val);
           }
    );
}

function change_item(e)
{
    var targ;
    if (!e) var e = window.event;
    if (e.target) targ = e.target;
    else if (e.srcElement) targ = e.srcElement;
    if (targ.nodeType == 3) // defeat Safari bug
        targ = targ.parentNode;
    change_state(targ);
}

function run_init()
{
    var tbl, rows, divs, div;

    $('#users tr:odd').each(function(ridx) {
        if (!$(this).hasClass("activeplayer"))
            $(this).addClass("odd");
    });

    if ('console' in self && 'log' in console)
    {
        logger = function(msg) {
            // console.log(msg);
        };
    }
    else
    {
        logger = function(msg) { };
    }

    $("#users tr").children("td").children("div").each(function(idx)
    {
        if ($(this).hasClass("player"))
        {
            logger("div.name " + this.attributes["name"]);
            init_div(this);
        }
    });

    $("#activeplayer div").each(function(idx) {
        this.onclick = change_item;
    });

    rows = document.getElementsByTagName("tr");
    logger(rows.length);
}

$(document).ready(function() {
    run_init();
});
