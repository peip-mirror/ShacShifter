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
    """The HTMLForm template bundle class."""

    def __init__(self):
        """Initialize an HTMLFormTemplateBundle object."""
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
        pass


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


class HTMLFormGroupItem(HTMLFormTemplate):
    """A template item of type "group"."""

    def __init__(self):
        """Initialize an HTMLFormGrouptItem object."""
        super().__init__()
        self.type = 'group'
        self.constraints = {}
        self.nodetype = ''
        self.items = []

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
        pass


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
        pass


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
        pass


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
            self.logger.error('Can''t write to file {}'.format(outputfile))
            self.logger.error('Content will be printed to sys.')

        for nodeShape in nodeShapes:
            form = self.createForm(nodeShapes[nodeShape])
            self.forms.append(form)

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

        def addFormItems():
            """Check Propertey Shapes to fill the templates."""
            addFormObjects = []
            for propertyShape in nodeShape.properties:
                formObject = self.getFormItem(propertyShape, nodeShape.nodeKind)
                if formItem is not None:
                    formItems.append(formItem)
            return formItem

        bundle = HTMLFormTemplateBundle()
        bundle.label = addNodeLabel()
        if nodeShape.isSet['message']:
            bundle.description = nodeShape.message
        bundle.root = nodeShape.uri
        if len(nodeShape.properties) > 0:
            bundle.templates = addFormItems()

        return bundle

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
            item = initTemplateItem()
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
            choiceItem.children = set(propertyShape.shIn) - set([choice])
            choices.append(choiceItem)

        return choices
