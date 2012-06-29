var map = new Object();
var table = [
    { "sp": "sprite-ellipsis", "msg": "awaiting response" },
    { "sp": "sprite-correct",  "msg": "I'm in!" },
    { "sp": "sprite-question", "msg": "Not sure yet.  I'll let you know soon." },
    { "sp": "sprite-wrong",    "msg": "No, not coming out." }
];

function change_state(div)
{
    var d = div.id;
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

function change_item(evt)
{
    change_state(evt.target);
}

function run_init()
{
    var divs, rows;

    divs = document.getElementsByName("player");
    for (var i=0; i < divs.length; i++)
    {
        divs[i].onclick = change_item;
        divs[i].id = "state_" + i;
        change_state(divs[i]);
    }

    rows = document.getElementsByClassName("users");
    console.log(rows.length);
}

window.onload = function()
{
    run_init();
}
