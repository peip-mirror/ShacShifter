

class StringSupplier:
    """Supplier for long Strings"""

    header = """<script src="https://bowercdn.net/c/urijs-1.19.1/src/URI.min.js"></script>
<form action="">
SPARQL Endpoint <br>
<input type="text" name="endpoint" value="{}"><br>
Ressource IRI <br>
<input type="text" name="ressourceIRI" value="{}"><br>
Graph (if empty equals http://example/Graph#) <br>
<input type="text" name="namedGraph" value="{}"><br>"""

    submit = """<br>
<input type="button" onclick="sendData(this.form)" value="Submit">
</form>"""

    script = """
<script>
if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function()
    {
        return String(this).replace(/^\\s+|\\s+$/g, '');
    };
}

function textfieldAdd(id, label) {
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    if(ancestor.dataset.max > 0 && descendents.length >= ancestor.dataset.max) {
        return;
    }
    var e, d, type, disableChoice, checked1, checked2, replacements;
    counter = descendents.length + 1;
    type = ancestor.dataset.type;
    if(type != "") {
        disableChoice = "disabled"
    }
    else {
        disableChoice = ""
    }
    if(disableChoice == "disabled"){
        checked1 = "";
        checked2 = "checked";
    }
    else {
        checked1 = "checked";
        checked2 = "";
    }
    replacements = {
    "%LABEL%": label,
    "%ID%": id + counter,
    "%BID%": id,
    "%CHOICE%": disableChoice,
    "%CHECKED1%": checked1,
    "%CHECKED2%": checked2};
    e = document.createElement('div');
    e.setAttribute('id', id + counter.toString());
    d = [
    '%LABEL%:<br>',
    '<input type="text" name="%ID%">',
    '<input type="radio" name="%ID%radio" %CHOICE% value="iri" %CHECKED1%>IRI',
    '<input type="radio" name="%ID%radio" %CHOICE% value="literal" %CHECKED2%>Literal',
    '<button type="button"',
    'onclick="textfieldDel(\\'%BID%\\', this.parentElement)">-</button>',
    '<br>'].join('\\n');
    d = d.replace(/%\\w+%/g, function(all) {
    return replacements[all] || all;});
    e.innerHTML = d;
    ancestor.appendChild(e);
}

function textfieldDel(id, delDiv){
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div'),
    min = ancestor.dataset.min;
    if(descendents.length <= min){
        // consider sending a message why
        return;
    }
    ancestor.removeChild(delDiv);
    fixIdValues(id)
}

function fixIdValues(id){
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    for (var i = 0; i < descendents.length; i++) {
        descendents[i].id = id + (i+1).toString();
        descendents[i].children[1].name = id + (i+1).toString();
        descendents[i].children[2].name = id + (i+1).toString() + "radio";
        descendents[i].children[3].name = id + (i+1).toString() + "radio";
    }
}

function sendData(form){
    if(form.endpoint.value.trim() === "" || form.ressourceIRI.value.trim() === "") {
        return;
    }
    //cant check for urls properly all regex solutions seem to be bad, use jquery? >only literals
    var triples = "",
    query = "",
    endpointURI = new URI(form.endpoint.value.trim()),
    ressourceURI = new URI(form.ressourceIRI.value.trim()),
    namedGraphURI = new URI(form.namedGraph.value.trim());
    if(!endpointURI.is("url") || !(ressourceURI.is("url") || ressourceURI.is("urn"))){
        return;
    }
    if(!form.namedGraph.value.trim === "" && !namedGraphURI.is("url")){
        return;
    }
    var inputs = form.getElementsByTagName('div');
    for (var i = 0; i < inputs.length; i++) {
        var subinputs = inputs[i].getElementsByTagName('div');
        for (var j = 0; j < subinputs.length; j++) {
            var object = new URI(subinputs[j].children[1].value.trim());
            if(object.is("url") || object.is("urn")){
                object = '<' + subinputs[j].children[1].value.trim() +  '>';
            }
            else {
                object = '"' + subinputs[j].children[1].value.trim() +  '"';
            }
            triples += '<' + form.ressourceIRI.value.trim() + '> <' + inputs[i].id +
                       '> "' + subinputs[j].children[1].value.trim() + '" . ';
        }
    }
    if(form.namedGraph.value === "") {
        query = "DELETE DATA { GRAPH <http://example/Graph#> {" + triples + "}};" +
                "INSERT DATA { GRAPH <http://example/Graph#> {" + triples + "}}";
    }
    else {
        query = "DELETE DATA { GRAPH <" + form.namedGraph.value.trim() + "> {" + triples + "}};" +
                "INSERT DATA { GRAPH <" + form.namedGraph.value.trim() + "> {" + triples + "}}";
    }
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            resultPresentation(this);
        }
    };
    alert(query);
    xhttp.open("POST", form.endpoint.value.trim(), true);
    xhttp.setRequestHeader("Content-Type", "application\/x-www-form-urlencoded");
    xhttp.send("update=" + encodeURIComponent(query));
}

function resultPresentation(result){
    alert(result);
}
</script>"""

    propertyMainDiv = """<div id="{}" data-min="{}" data-max="{}" data-type="{}">"""

    propertySubDiv = """<div id="{id}">{0}:<br>
<input type="text" name="{id}">
<input type="radio" name="{id}radio" {choice} value="iri" {1}>IRI
<input type="radio" name="{id}radio" {choice} value="literal" {2}>Literal
<button type="button" onclick="textfieldDel('{3}', this.parentElement)">-</button>
<br>
</div>"""

    propertyMainDivClose = """</div>
<button type="button" onclick="textfieldAdd('{}', '{}')">+</button>"""

    choiceInput = """<input type="radio" name="{}" value="{}"> {}<br>"""

    jqueryCDN = """<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>"""