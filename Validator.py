Python 3.11.3 (tags/v3.11.3:f3909b8, Apr  4 2023, 23:49:59) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
"""    Defines custom Maya based validators
"""
import re
import os

 

import mpc.logging
from mpc.pyCore.validators import (
    ValidationError as _ValidationError,
    ValueIsNonEmptyStringValidator as _ValueIsNonEmptyStringValidator,
    DirectoryExistsValidator as _DirectoryExistsValidator
)

 

_log = mpc.logging.getLogger()
_modelPattern = '(?P<modelNameWithVariation>(?P<modelName>[a-z][a-zA-Z0-9]+)(?P<modelVariation>[A-Z]))'

 

 

class _BaseStringValidator(object):
    """ A validator to check that the value is valid string, Which is not empty.

 

        Args:
            value (basestring): The value to validate

 

        Raises:
            A Validation exception if value contains
            invalid string or empty string.
    """
    def __call__(self, value):
        try:
            _ValueIsNonEmptyStringValidator()(value)
        except _ValidationError as err:
            raise _ValidationError('The assetName give is not a valid string.(%s)' % err)

 

 

class BaseAssetNameValidator(_BaseStringValidator):
    """ Validate the either the name contains "element" or not.

 

        Args:
            value (basestring): The string value to validate.

 

        Raises:
            A Validation exception if value contains "element".
    """
    _patterns = []

    def __init__(self):
        super( BaseAssetNameValidator, self ).__init__()
        self._result = {}

 

    def __call__(self, value):
        super(BaseAssetNameValidator, self ).__call__(value)
        regEx = re.compile('(.+element(.+|$))', re.IGNORECASE)
        if regEx.match(value):
            raise _ValidationError('The assetName given(%s) contains "element".' % value)

 

        flag = False
        for pattern in self._patterns:
            reOutput = re.compile('^%s$' % pattern).match(value)
            if reOutput:
                self._result = reOutput.groupdict()
                flag = True
                break

 

        if not flag:
            raise _ValidationError(
                'The given value(%s) is not a valid name.' % value
            )

 

    @property
    def result(self):
        """ Return the result of the regular expression.

 

            Returns:
                (dict): keys and values of the regular expression groups.
        """
        return self._result

 

 

class MayaModelGroupNameValidator(BaseAssetNameValidator):
    """ Validator class for the modelGroup name in maya.
    """
    _patterns = [
        '%s(_lod(?P<levelOfDetail>[A-D]))_GRP' % _modelPattern,
    ]

 

 

class PrimaryPackageNameValidator(BaseAssetNameValidator):
    """ Validator class for the unstreamed primary model package name asset.
    """
    _patterns = [
        '(?P<element>%s)' % _modelPattern
    ]

 

 

class ModelNameValidator(BaseAssetNameValidator):
    """ Validator class for the model asset.
    """
    _patterns = [
        '(?P<element>%s(_lod(?P<levelOfDetail>[A-D])))' % _modelPattern
    ]

 

 

class BaseModelPkgNameValidator(BaseAssetNameValidator):
    """ Validator class for the BaseModelPkg asset.
    """
    _patterns = [
        '((?P<stream>\w+)STR|)(?P<element>%s)' % _modelPattern
    ]

 

 

class ModelPkgNameValidator(BaseAssetNameValidator):
    """ Validator class for the ModelPkg asset.
    """
    _patterns = [
        '((?P<stream>\w+)STR|)(?P<element>%s(v(?P<textureVariation>[A-Z]+)))' % _modelPattern
    ]

 

 

class CharacterTypePkgNameValidator(BaseAssetNameValidator):
    """ Validator class for the CharacterTypePkg asset.
    """
    _patterns = [
...         '((?P<stream>\w+)STR|)(?P<element>%s)' % _modelPattern
...     ]
... 
...  
... 
...  
... 
... class CharacterPkgNameValidator(BaseAssetNameValidator):
...     """ Validator class for the CharacterPkg asset.
...     """
...     _patterns = [
...         '((?P<stream>\w+)STR|)(?P<element>%s(v(?P<textureVariation>[A-Z]+)))' % _modelPattern
...     ]
... 
...  
... 
...  
... 
... class WritableTargetPathValidator(_DirectoryExistsValidator):
...     """    Validate the directory is writable
...     """
...     def __call__(self, value):
...         super(WritableTargetPathValidator, self).__call__(value)
... 
...         if not os.access(value, os.W_OK):
...             raise _ValidationError('Directory %s is not writable' % (value, ))
... 
...  
... 
...  
... 
... _typeValidatorMap = {
...     'mayaModelGroup': MayaModelGroupNameValidator,
...     'model': ModelNameValidator,
...     'PrimaryPackageName': PrimaryPackageNameValidator,
...     'BaseModelPkg': BaseModelPkgNameValidator,
...     'ModelPkg': ModelPkgNameValidator,
...     'CharacterTypePkg': CharacterTypePkgNameValidator,
