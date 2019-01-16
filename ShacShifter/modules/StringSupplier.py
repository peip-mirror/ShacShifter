

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
<input type="button" id="submitbutton" onclick="sendData(this.form)" value="Submit" disabled>
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
    '<input type="text" name="%ID%" onkeyup="checkValidity(this.parentElement)">',
    '<input type="radio" name="%ID%radio" %CHOICE% value="iri" onclick="checkValidity(this.parentElement)" %CHECKED1%>IRI',
    '<input type="radio" name="%ID%radio" %CHOICE% value="literal" onclick="checkValidity(this.parentElement)" %CHECKED2%>Literal',
    '<button type="button"',
    'onclick="textfieldDel(\\'%BID%\\', this.parentElement)">-</button>',
    '<br>'].join('\\n');
    d = d.replace(/%\\w+%/g, function(all) {
    return replacements[all] || all;});
    e.innerHTML = d;
    ancestor.appendChild(e);
    checkValidity(e);
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
            var object = subinputs[j].children[1].value.trim();
            if(subinputs[j].children[2].checked){
                object = '<' + object +  '>';
            }
            else {
                object = '"' + object +  '"';
            }
            triples += '<' + form.ressourceIRI.value.trim() + '> <' + inputs[i].id +
                       '> ' + object + ' . ';
        }
    }
    if(form.namedGraph.value === "") {
        query = "DELETE { <" + form.ressourceIRI.value.trim() + "> ?p ?o} WHERE { <" + form.ressourceIRI.value.trim() + "> ?p ?o . }" +
                "INSERT DATA {" + triples + "}";
    }
    else {
        query = "DELETE { GRAPH <" + form.namedGraph.value.trim() + ">  {<" + form.ressourceIRI.value.trim() + "> ?p ?o}} WHERE { GRAPH <" + form.namedGraph.value.trim() + "> {<" + form.ressourceIRI.value.trim() + "> ?p ?o . }};" +
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

function checkValidity(subDiv){
    if(subDiv.children[2].checked) {
        var objectURI = new URI(subDiv.children[1].value.trim())
        if(!(objectURI.is("url") || objectURI.is("urn"))){
            subDiv.children[1].backgroundColor = "red"
            subDiv.dataset.correct = ""
        }
        else{
            subDiv.children[1].backgroundColor = "white"
            subDiv.dataset.correct = "correct"
        }
    }
    else {
        //future check for string types, potentially string length etc etc
        subDiv.children[1].backgroundColor = "white"
        subDiv.dataset.correct = "correct"
    }
    checkMainDivValidity(subDiv.parentElement)
}

function checkMainDivValidity(mainDiv){
    var subDivs = mainDiv.getElementsByTagName("div"),
    allSDivsCorrect = true;
    for(var i = 0; i < subDivs.length; i++) {
        if(subDivs[i].dataset.correct == "") {
            allSDivsCorrect = false;
        }
    }
    if(allSDivsCorrect){
        mainDiv.dataset.correct = "correct";
    }
    checkFormValidity(mainDiv.parentElement);
}

function checkFormValidity(form){
    var mainDivs = form.getElementsByTagName('div'),
    allMDivsCorrect = true;
    for (var i = 0; i < mainDivs.length; i++) {
        if(mainDivs[i].dataset.correct == "") {
            allMDivsCorrect = false;
        }
    }
    if(allMDivsCorrect){
        document.getElementById("submitbutton").disabled = false
    }
    else{
        document.getElementById("submitbutton").disabled = true
    }
}
</script>"""

    propertyMainDiv = """<div id="{}" data-min="{}" data-max="{}" data-type="{}" data-correct="">"""

    propertySubDiv = """<div id="{id}" data-correct="">{0}:<br>
<input type="text" name="{id}" onkeyup="checkValidity(this.parentElement)">
<input type="radio" name="{id}radio" {choice} value="iri" onclick="checkValidity(this.parentElement)" {1}>IRI
<input type="radio" name="{id}radio" {choice} value="literal" onclick="checkValidity(this.parentElement)" {2}>Literal
<button type="button" onclick="textfieldDel('{3}', this.parentElement)">-</button>
<br>
</div>"""

    propertyMainDivClose = """</div>
<button type="button" onclick="textfieldAdd('{}', '{}')">+</button>"""

    choiceInput = """<input type="radio" name="{}" value="{}"> {}<br>"""

    jqueryCDN = """<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>"""
