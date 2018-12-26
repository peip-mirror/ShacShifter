from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .modules.StringSupplier import StringSupplier
from .ShapeParser import ShapeParser
import logging


class HTMLPart:
    """A super class that provides some methods."""
    def __str__(self):
        """Print HTMLFormTemplate object."""
        return ', '.join(['%s: %s' % (key, value) for (key, value) in self.__dict__.items()])

    def toHTML(self):
        # TODO consider BeautifulSoup for indention
        return self.htmlRepr()

    def htmlRepr(self):
        """Build HTML"""
        pass


class HTMLForm(HTMLPart):
    """The HTMLForm class."""
    def __init__(self, endpoint, ressourceIRI, namedGraph):

        """Initialize an HTMLForm object."""
        self.label = ''
        self.description = {}
        self.root = ''
        self.formItems = []
        self.endpoint = endpoint
        self.ressourceIRI = ressourceIRI
        self.namedGraph = namedGraph

    def __str__(self):
        """Print HTMLFormTemplate object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'formItems':
                printdict[key] = [str(template) for template in value]
            else:
                printdict[key] = value
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def htmlRepr(self):
        """Build HTML"""
        plainHTML = """<script src="https://bowercdn.net/c/urijs-1.19.1/src/URI.min.js"></script>
<form action="">
SPARQL Endpoint <br>
<input type="text" name="endpoint" value="{}"><br>
Ressource IRI <br>
<input type="text" name="ressourceIRI" value="{}"><br>
Graph (if empty equals http://example/Graph#) <br>
<input type="text" name="namedGraph" value="{}"><br>""".format(self.endpoint, self.ressourceIRI,
                                                               self.namedGraph)
        for item in self.formItems:
            plainHTML += item.htmlRepr()
        plainHTML += """<br><input type="button" onclick="sendData(this.form)" value="Submit">
</form>"""
        plainHTML += """
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
        return plainHTML


class HTMLFormTemplate(HTMLPart):
    """The HTMLForm template (super)class."""

    def __init__(self):
        """Initialize an HTMLFormTemplate object."""
        self.id = ''
        self.label = ''
        self.description = {}
        self.property = ''
        self.cardinality = {'min': 0, 'pref': 0}

    def htmlRepr(self):
        """Build HTML"""
        pass


class HTMLFormTextItem(HTMLFormTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an HTMLFormTextItem object."""
        super().__init__()
        self.cardinality = {'min': 0, 'pref': 1}
        self.type = 'text'
        self.nodeKind = ''
        self.datatype = ''

    def htmlRepr(self):
        """Build HTML"""
        maxSet = False
        if 'max' in self.cardinality:
            maxSet = True
        plainHTML = """<div id="{}" data-min="{}" data-max="{}" data-type="{}">""".format(
            self.id, self.cardinality['min'], self.cardinality['max'] if maxSet else 0,
            self.datatype)
        disableChoice = 'disabled' if self.datatype != '' else ''
        counter = 1
        while counter <= self.cardinality['pref']:
            if maxSet and counter >= self.cardinality['max'] + 1:
                break

            plainHTML += """<div id="{}">{}:<br>
<input type="text" name="{}"><input type="radio" name="{}radio" {} value="iri" {}>IRI
<input type="radio" name="{}radio" {} value="literal" {}>Literal
<button type="button" onclick="textfieldDel('{}', this.parentElement)">-</button>
<br></div>""".format(self.id + str(counter), self.label, self.id + str(counter),
                self.id + str(counter), disableChoice, 'checked' if not disableChoice else '',
                self.id + str(counter), disableChoice, 'checked' if disableChoice else '', self.id)
            counter += 1
        plainHTML += """</div><button type="button" onclick="textfieldAdd('{}', '{}')">+</button>
""".format(self.id, self.label)
        return plainHTML


class HTMLFormChoiceItem(HTMLFormTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an HTMLFormChoiceItem object."""
        super().__init__()
        self.type = 'choice'
        self.constraints = {}
        self.nodeKind = ''
        self.choices = []

    def __str__(self):
        """Print HTMLFormChoiceItem object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'choices':
                printdict[key] = [str(choice) for choice in value]
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def htmlRepr(self):
        """Build HTML"""
        plainHTML = ""
        for choice in sorted(self.choices, key=lambda x: x.value, reverse=True):
            plainHTML += choice.htmlRepr()
        return plainHTML


class HTMLFormChoiceExpression(HTMLPart):
    """A class for choice expressions."""

    def __init__(self):
        """Initialize an HTMLFormChoiceExpression object."""
        self.value = ''
        self.label = ''
        self.description = ''
        self.selectable = True

    def __str__(self):
        """Print HTMLFormChoiceExpression object."""
        printdict = {}
        for key, value in self.__dict__.items():
            if key == 'children':
                printdict[key] = [str(child) for child in value]
            else:
                printdict[key] = value
        return ', '.join(['%s: %s' % (key, value) for (key, value) in printdict.items()])

    def htmlRepr(self):
        """Build HTML"""
        plainHTML = """ <input type="radio" name="{}" value="{}"> {}<br>""".format(
                self.label, self.label, self.label)


class HTMLSerializer:
    """A Serializer that writes HTML."""

    logger = logging.getLogger('ShacShifter.HTMLSerializer')
    forms = []
    outputfile = None

    def __init__(self, nodeShapes, outputfile=None, endpoint="", ressourceIRI="", namedGraph=""):
        """Initialize the Serializer and parse des ShapeParser results.

        args: shapes
              string outputfile
              string endpoint
              string ressourceIRI
              string namedGraph
        """
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close()
        except Exception:
            self.logger.error('Can\'t write to file {}'.format(outputfile))
            self.logger.error('Content will be printed to sys.')

        self.nodeShapes = nodeShapes
        self.endpoint = "" if (endpoint is None) else endpoint
        self.ressourceIRI = "" if (ressourceIRI is None) else ressourceIRI
        self.namedGraph = "" if (namedGraph is None) else namedGraph

        counter = 0
        for nodeShape in nodeShapes:
            if counter == 0:
                form = self.createForm(nodeShapes[nodeShape])
                self.forms.append(form)
            else:
                self.logger.info('HTMLSerializer only supports displaying one Nodeshape.')
            counter += 1

    def write(self):
        """Write HTMLForm to file or sysout."""
        jquery = """<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquer\
y.min.js"></script>
"""
        if self.outputfile:
            fp = open(self.outputfile, 'w')
            for form in self.forms:
                htmlForm = form.toHTML()
                print(htmlForm)
                fp.write(jquery)
                fp.write(htmlForm + '\n')
            fp.close()
        else:
            for form in self.forms:
                print(jquery)
                print(form.toHTML())

    def createForm(self, nodeShape):
        """Evaluate a nodeShape.

        args:   NodeShape nodeShape
        """
        def addNodeLabel():
            label = 'Template: ' + nodeShape.uri
            if nodeShape.isSet['targetClass']:
                label = 'Create new Instance of: ' + ', '.join(nodeShape.targetClass)
            if nodeShape.isSet['targetNode']:
                label = 'Edit Instance of: ' + ', '.join(nodeShape.targetNode)
            if nodeShape.isSet['targetObjectsOf']:
                label = ', '.join(nodeShape.targetObjectsOf)
            if nodeShape.isSet['targetSubjectsOf']:
                label = 'Edit: '', '.join(nodeShape.targetSubjectsOf)
            return label

        def addFormItems(nodeShape):
            """Check Propertey Shapes to fill the templates."""
            formItems = []
            for propertyShape in nodeShape.properties:
                formItem = self.getFormItem(propertyShape, nodeShape.nodeKind)
                if formItem is not None:
                    formItems.append(formItem)
                    if propertyShape.isSet['nodes']:
                        subFormItems = []
                        for node in propertyShape.nodes:
                            subFormItems.extend(addFormItems(self.nodeShapes[node]))
                        if len(subFormItems) > 0:
                            formItems.extend(subFormItems)
            return formItems

        form = HTMLForm(self.endpoint, self.ressourceIRI, self.namedGraph)
        form.label = addNodeLabel()
        if nodeShape.isSet['message']:
            form.description = nodeShape.message
        form.root = nodeShape.uri
        if len(nodeShape.properties) > 0:
            form.formItems = addFormItems(nodeShape)
        return form

    def getFormItem(self, propertyShape, nodeKind):
        """Evaluate a propertyShape to serialize a formObject section.

        args:   PropertyShape propertyShape
        return: HTMLFormItem
        """
        def initFormItem():
            if propertyShape.isSet['shIn']:
                item = fillChoiceItem(HTMLFormChoiceItem())
            else:
                item = fillTextItem(HTMLFormTextItem())

            return fillBasicItemValues(item)

        def fillChoiceItem(item):
            item = fillBasicItemValues(item)
            item.cardinality = getCardinality()
            item.choices = self.getChoices(propertyShape)
            return item

        def fillTextItem(item):
            item.cardinality = getCardinality()
            if propertyShape.isSet['datatype']:
                item.datatype = propertyShape.datatype
            return item

        def fillBasicItemValues(item):
            item.id = propertyShape.path
            item.label = propertyShape.name if propertyShape.isSet['name'] else (
                                    propertyShape.path.rsplit('/', 1)[-1])
            item.description = getDescription()
            item.nodeKind = nodeKind
            return item

        def getDescription():
            if propertyShape.isSet['message']:
                if 'en' in propertyShape.message:
                    return propertyShape.message['en']
                elif 'default' in propertyShape.message:
                    return propertyShape.message['default']
            elif propertyShape.isSet['description']:
                return {'en': propertyShape.description}
            else:
                return {'en': 'This is about ' + propertyShape.path}

        def getCardinality():
            cardinality = {'min': 0, 'pref': 1}

            if propertyShape.isSet['minCount']:
                cardinality['min'] = propertyShape.minCount

            if propertyShape.isSet['maxCount']:
                cardinality['max'] = propertyShape.maxCount

            return cardinality

        if isinstance(propertyShape.path, dict):
            # TODO handle complex paths (inverse, oneOrMorePath ...)
            self.logger.info('Complex path not supported, yet')
        elif isinstance(propertyShape.path, list):
            # TODO handle sequence paths
            self.logger.info('Sequence path not supported, yet')
        else:
            item = initFormItem()
            return item

    def getChoices(self, propertyShape):
        """Search for choice candidates in propertyShape and return a choice list.

        args: PropertyShape propertyShape
        returns: list
        """
        choices = []
        for choice in propertyShape.shIn:
            choiceItem = HTMLChoiceExpression()
            choiceItem.label = choice
            choiceItem.value = choice
            choices.append(choiceItem)

        return choices
