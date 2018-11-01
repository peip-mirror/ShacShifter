from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
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

    def __init__(self):
        """Initialize an HTMLForm object."""
        self.label = ''
        self.description = {}
        self.root = ''
        self.formItems = []

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
        plainHTML = """<form action="/action.php">"""
        for item in self.formItems:
            plainHTML += item.htmlRepr()
        plainHTML += """<br><input type="submit" value="Submit">
</form>"""
        plainHTML += """
<script>
function textfieldAddMax(id) {
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    var i;
    for (i = 0; i < descendents.length; ++i) {
        if (descendents[i].style.display === 'none') {
            descendents[i].style.display = 'inline';
            break;
        }
    }
}
function textfieldAdd(id, label) {
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    var e, d, replacements;
    counter = descendents.length + 1;
    replacements = {
    "%LABEL%": label,
    "%ID%": id + counter};
    e = document.createElement('div');
    e.setAttribute('id', id + counter.toString());
    d = [
    '%LABEL%:<br>',
    '<input type="text" name="%ID%"><br>'].join('\\n');
    d = d.replace(/%\\w+%/g, function(all) {
    return replacements[all] || all;});
    e.innerHTML = d;
    ancestor.appendChild(e);
}
function textfieldDelMax(id){
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    var i;
    for (i = 0; i < descendents.length; ++i) {
        if (descendents[i].style.display === 'none') {
            if (i > 0) {
                descendents[i - 1].style.display = 'none'
            }
            break;
        }
        else if(i === (descendents.length -1)) {
            descendents[i].style.display = 'none'
            break;
        }
    }
}
function textfieldDel(id){
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    var e = document.getElementById(id + descendents.length.toString());
    if(descendents.length > 1) {
        ancestor.removeChild(e);
    }
}
</script> """
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
        self.nodetype = ''

    def htmlRepr(self):
        """Build HTML"""
        plainHTML = """<div id="{}">""".format(self.id)
        if 'max' in self.cardinality:
            counter = 1
            while counter <= self.cardinality['max']:
                if counter <= self.cardinality['pref']:
                    style = ''
                else:
                    style = 'style="display:none"'
                plainHTML += """<div {} id="{}">{}:<br>
<input type="text" name="{}"><br></div>""".format(
                    style, self.id + str(counter), self.label, self.id + str(counter))
                counter += 1
            plainHTML += """</div><button type="button" onclick="textfieldAddMax('{}')">+</button>
<button type="button" onclick="textfieldDelMax('{}')">-</button>""".format(self.id, self.id)
        else:  # how should no maximum be handled? allow infinite new textbars through js?
            plainHTML += """<div id="{}">{}:<br>
<input type="text" name="{}"><br></div>""".format(self.id + '1', self.label, self.id + '1')
            plainHTML += """</div><button type="button" onclick="textfieldAdd('{}', '{}')">+</button>
<button type="button" onclick="textfieldDel('{}')">-</button>""".format(self.id, self.label, self.id)
        return plainHTML


class HTMLFormChoiceItem(HTMLFormTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an HTMLFormChoiceItem object."""
        super().__init__()
        self.type = 'choice'
        self.constraints = {}
        self.nodetype = ''
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

    def __init__(self, nodeShapes, outputfile=None):
        """Initialize the Serializer and parse des ShapeParser results.

        args: shapes
              string outputfile
        """
        try:
            fp = open(outputfile, 'w')
            self.outputfile = outputfile
            fp.close()
        except Exception:
            self.logger.error('Can\'t write to file {}'.format(outputfile))
            self.logger.error('Content will be printed to sys.')

        self.nodeShapes = nodeShapes

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
        if self.outputfile:
            fp = open(self.outputfile, 'w')
            for form in self.forms:
                htmlForm = form.toHTML()
                print(htmlForm)
                fp.write(htmlForm + '\n')
            fp.close()
        else:
            for form in self.forms:
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

        form = HTMLForm()
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
            return item

        def fillBasicItemValues(item):
            item.id = propertyShape.path
            item.label = propertyShape.name if propertyShape.isSet['name'] else (
                                    propertyShape.path.rsplit('/', 1)[-1])
            item.description = getDescription()
            item.nodetype = nodeKind
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
