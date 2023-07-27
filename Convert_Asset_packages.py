Python 3.11.3 (tags/v3.11.3:f3909b8, Apr  4 2023, 23:49:59) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.

import argparse
import sys

import logging
from tessa import store, uri, legacy
from readPackageAPI.readCommon import ReadStore
from readPackageAPI.readPackage import ReadPackage
from assetTools.utilities import pipeline as _utilsPipeline
from assetTools.utilities import packaging as _packaging

_log = logging.getLogger()

_assetTypes = ("CharacterTypePkg", "CharacterPkg", "BaseModelPkg", "ModelPkg")

_baseLocations = {
    "CharacterPkg": ("CharacterType", "characterType"),
    "ModelPkg": ("BaseModel", "baseModel"),
}

_dataLocations = {
    "CharacterTypePkg": {
        "model": [
            ("Hero", ["model"], False),
            ("VariationsOptions", ["key", "variationSettings"], True),
        ],
        "texture": [
            ("HeroTexture", ["key", "texture"], True)
        ],
    },
    "CharacterPkg": {
        "model": [
            ("VariationSettings", ["key"], True)
        ],
        "texture": [
            ("TextureSettings", ["heroKey"], True)
        ],
    },
    "BaseModelPkg": {
        "model": [
            ("LodA", ["model"], False),
            ("VariationsOptions", ["key", "lodAVariationSettings"], True),
        ],
        "texture": [
            ("Textures", ["key", "lodATexturePackage"], True),
        ],
    },
    "ModelPkg": {
        "model": [
            ("VariationSettings", ["key"], True),
        ],
        "texture": [
            ("TextureSettings", ["key"], True),
        ],
    },
}

_targetMapping = {
    "ModelPkg": "CharacterPkg",
    "BaseModelPkg": "CharacterTypePkg",
    "CharacterPkg": "ModelPkg",
    "CharacterTypePkg": "BaseModelPkg",
}

_mappingsModelToChar = (
    (("LodA", "model"), ("Hero", "model")),
    (("VariationsOptions", "key"), ("VariationsOptions", "key")),
    (("VariationsOptions", "lodAVariationSettings"), ("VariationsOptions", "variationSettings")),
    (("Textures", "key"), ("HeroTexture", "key")),
    (("Textures", "lodATexturePackage"), ("HeroTexture", "texture")),
    (("VariationSettings", "key"), ("VariationSettings", "key")),
    (("TextureSettings", "key"), ("TextureSettings", "heroKey")),
)

_locationMappings = {
    "CharacterPkg": dict((mpLoc, cpLoc) for mpLoc, cpLoc in _mappingsModelToChar),
    "CharacterTypePkg": dict((mpLoc, cpLoc) for mpLoc, cpLoc in _mappingsModelToChar),
    "ModelPkg": dict((cpLoc, mpLoc) for mpLoc, cpLoc in _mappingsModelToChar),
    "BaseModelPkg": dict((cpLoc, mpLoc) for mpLoc, cpLoc in _mappingsModelToChar),
}

class MigrationAsset(object):  # pylint: disable=R0902
    """ Class to describe the migration plan for a
        source texture stream asset
    """

    def __init__(self, sourceAssetVersion):
        super(MigrationAsset, self).__init__()

        # Define texture stream data members
        self.sourceAssetVersion = sourceAssetVersion
        self.uri = uri.fromAssetVersion(self.sourceAssetVersion)
        self.assetType = sourceAssetVersion.assetType
        self.targetType = _targetMapping[self.sourceAssetVersion.assetType]
        self.sourceReadPackage = _utilsPipeline.getReadPackage(sourceAssetVersion)

        # Define target members
        self.targetReadPackage = None
        self.targetAsset = store.Asset(
            context=self.sourceAssetVersion.context,
            assetType=self.targetType,
            name=self.sourceAssetVersion.name,
            stream=self.sourceAssetVersion.stream,
        )

    def __repr__(self):
        return "<MigrationAsset for {0}>".format(self.uri)

    def matchContents(self, packagingComments):
        """ Compares the contents of the textureSTR package and ensures
            the modelSTR package matches it
            Args:
                packagingComments (list): Comments of work done
        """
        # Define components to match
        for location in _dataLocations[self.assetType].get(self.sourceAssetVersion.stream.name, []):
            self.matchLocationContents(location, packagingComments)

    def matchLocationContents(self, location, packagingComments):
...         """ Matches contents of texture stream in the model stream.
...             Args:
...                 location (tuple): Component str, Field str, is a multi row bool.
...                 packagingComments (list): List to append comments of work done.
...         """
...         componentName, fieldNames, multiRow = location
...         targetComponentName, _ = _locationMappings[self.targetType][(componentName, fieldNames[0])]
... 
...         # Populate component
...         targetComponent = self.targetReadPackage[targetComponentName]
...         if multiRow:
...             _packaging.matchRowCount(targetComponent, len(self.sourceReadPackage[componentName]))
...             for index, row in enumerate(targetComponent):
...                 rowIdx = index + 1
...                 for fieldName in fieldNames:
...                     _, targetFieldName = _locationMappings[self.targetType][(componentName, fieldName)]
...                     _packaging.checkFieldValue(
...                         row[targetFieldName],
...                         self.sourceReadPackage[componentName][rowIdx][fieldName].value(),
...                         packagingComments
...                     )
...         else:
...             for fieldName in fieldNames:
...                 _, targetFieldName = _locationMappings[self.targetType][(componentName, fieldName)]
...                 _packaging.checkFieldValue(
...                     targetComponent[targetFieldName],
...                     self.sourceReadPackage[componentName][fieldName].value(),
...                     packagingComments
...                 )
... 
...     def createTarget(self, packagingComments):
...         """ Establishes a model STR variation of the texture STR and
...             copies across the model data
...             Args:
...                 packagingComments (list): Comments of work done
...         """
...         pkgVersion = "new" if not _utilsPipeline.doesAssetExist(self.targetAsset) else "preferLatest"
...         self.targetReadPackage = ReadPackage.fromDotNotation(
...             ".".join((
...                 self.targetAsset.context.job.name,
...                 self.targetAsset.context.scene.name,
...                 self.targetAsset.context.shot.name,
...                 self.targetAsset.assetType,
...                 legacy.joinStreamWithAssetName(
...                     self.targetAsset.name,
...                     self.targetAsset.stream
...                 ),
...                 pkgVersion,
...             ))
...         )
...         if pkgVersion == "new":
...             logMsg = "# {0} : Created {1}".format(
...                 _utilsPipeline.representAsset(self.targetReadPackage),
...                 self.targetReadPackage.bundle()
...             )
...             logging.info(logMsg)
...             packagingComments.append(logMsg)
... 
... def _getBasePackage(packageVersion):
...     """ Find the base package of input package version
...         Args:
...             packageVersion : instant to represent the asset version
...     """
...     for location, dependency in packageVersion.dependencies():
...         if packageVersion.assetType == "CharacterPkg" and location == ("CharacterType", 0, "characterType"):
...             return dependency
...         if packageVersion.assetType == "ModelPkg" and location == ("BaseModel", 
