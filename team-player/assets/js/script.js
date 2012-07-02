var map = new Object();
var table = [
    { "sp": "sprite-ellipsis", "msg": "awaiting response" },
    { "sp": "sprite-correct",  "msg": "I'm in!" },
    { "sp": "sprite-question", "msg": "Not sure yet.  I'll let you know soon." },
    { "sp": "sprite-wrong",    "msg": "No, not coming out." }
];

var logger;

function change_state(div)
{
    var d = div.id;
    logger("ClientID: " + d);
    if (map[d] === undefined) {
        map[d] = 0;
    }
    div.title = table[map[d]]["msg"];
    div.className = "sprites " + table[map[d]]["sp"];
    if (map[d] == table.length - 1)
        map[d] = 0;
    else
        map[d] += 1;
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
            //console.log(msg);
        };
    }
    else
    {
        logger = function(msg) { };
    }

    tbl = document.getElementById("users");

    divs = tbl.getElementsByTagName("div");
    for (var i=0; i < divs.length; i++)
    {
        div = divs[i];
        logger("div.name " + div.attributes["name"]);
        div.onclick = change_item;
        div.id = "state_" + i;
        change_state(div);
    }

    rows = document.getElementsByTagName("tr");
    logger(rows.length);
}

$(document).ready(function() {
    run_init();
});
