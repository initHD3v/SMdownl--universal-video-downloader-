#!/usr/bin/env python3
"""
Generate Xcode project for SMDown_M
Simplified version for Xcode 15+/26+
"""

import os
import uuid
import plistlib
from pathlib import Path

def generate_uuid():
    """Generate a 24-character hex UUID like Xcode does"""
    return uuid.uuid4().hex[:24].upper()

class XcodeProjectGenerator:
    def __init__(self, project_name, bundle_id):
        self.project_name = project_name
        self.bundle_id = bundle_id
        self.objects = {}
        self.root_group_children = []
        self.source_build_files = []
        self.resource_build_files = []

    def create_file_reference(self, path, file_type):
        """Create a PBXFileReference"""
        uuid_hex = generate_uuid()
        self.objects[uuid_hex] = {
            'isa': 'PBXFileReference',
            'lastKnownFileType': file_type,
            'path': os.path.basename(path),
            'sourceTree': '<group>'
        }
        return uuid_hex

    def create_build_file(self, file_ref_uuid):
        """Create a PBXBuildFile"""
        uuid_hex = generate_uuid()
        self.objects[uuid_hex] = {
            'isa': 'PBXBuildFile',
            'fileRef': file_ref_uuid
        }
        return uuid_hex

    def create_group(self, name, path=None, children=None):
        """Create a PBXGroup"""
        uuid_hex = generate_uuid()
        self.objects[uuid_hex] = {
            'isa': 'PBXGroup',
            'children': children or [],
            'sourceTree': '<group>'
        }
        if name:
            self.objects[uuid_hex]['name'] = name
        if path:
            self.objects[uuid_hex]['path'] = path
        return uuid_hex

    def _get_file_type(self, path):
        """Determine file type from extension"""
        ext = os.path.splitext(path)[1].lower()
        types = {
            '.swift': 'sourcecode.swift',
            '.plist': 'text.plist.xml',
            '.xcassets': 'folder.assetcatalog',
            '.entitlements': 'text.plist.entitlements',
            '.storyboard': 'file.storyboard',
            '.xib': 'file.xib',
            '.md': 'text',
            '.swiftinterface': 'sourcecode.swift',
        }
        return types.get(ext, 'text')

    def add_source_file(self, rel_path, group_uuid):
        """Add a source file to a group"""
        file_ref = self.create_file_reference(rel_path, self._get_file_type(rel_path))
        build_file = self.create_build_file(file_ref)
        self.source_build_files.append(build_file)
        
        # Add to group
        self.objects[group_uuid]['children'].append(file_ref)
        return file_ref

    def add_resource_file(self, rel_path, group_uuid):
        """Add a resource file to a group"""
        file_ref = self.create_file_reference(rel_path, self._get_file_type(rel_path))
        build_file = self.create_build_file(file_ref)
        self.resource_build_files.append(build_file)
        
        # Add to group
        self.objects[group_uuid]['children'].append(file_ref)
        return file_ref

    def generate(self, output_path):
        """Generate the complete project file"""
        smdown_dir = os.path.join(output_path, self.project_name)

        # Generate UUIDs for main structure
        project_uuid = generate_uuid()
        main_group_uuid = generate_uuid()
        products_group_uuid = generate_uuid()
        
        # Target and build phases
        target_uuid = generate_uuid()
        build_config_list_project_uuid = generate_uuid()
        build_config_list_target_uuid = generate_uuid()
        debug_config_uuid = generate_uuid()
        release_config_uuid = generate_uuid()
        debug_target_config_uuid = generate_uuid()
        release_target_config_uuid = generate_uuid()
        sources_phase_uuid = generate_uuid()
        frameworks_phase_uuid = generate_uuid()
        resources_phase_uuid = generate_uuid()
        product_uuid = generate_uuid()

        # Create main group structure
        app_group_uuid = self.create_group(None, path=self.project_name)
        views_group_uuid = self.create_group('Views', path='Views')
        viewmodels_group_uuid = self.create_group('ViewModels', path='ViewModels')
        models_group_uuid = self.create_group('Models', path='Models')
        services_group_uuid = self.create_group('Services', path='Services')
        downloader_group_uuid = self.create_group('Downloader', path='Downloader')
        utils_group_uuid = self.create_group('Utils', path='Utils')
        resources_group_uuid = self.create_group('Resources', path='Resources')

        # Set up app group children
        self.objects[app_group_uuid]['children'] = [
            views_group_uuid,
            viewmodels_group_uuid,
            models_group_uuid,
            services_group_uuid,
            downloader_group_uuid,
            utils_group_uuid,
            resources_group_uuid
        ]

        # Set up main group
        self.objects[main_group_uuid] = {
            'isa': 'PBXGroup',
            'children': [app_group_uuid, products_group_uuid],
            'sourceTree': '<group>'
        }

        # Products group
        self.objects[products_group_uuid] = {
            'isa': 'PBXGroup',
            'children': [product_uuid],
            'name': 'Products',
            'sourceTree': '<group>'
        }

        # Product reference
        self.objects[product_uuid] = {
            'isa': 'PBXFileReference',
            'explicitFileType': 'wrapper.application',
            'includeInIndex': 0,
            'path': f'{self.project_name}.app',
            'sourceTree': 'BUILT_PRODUCTS_DIR'
        }

        # Find and add all Swift files
        for root, dirs, files in os.walk(smdown_dir):
            # Skip certain directories
            if '__pycache__' in root or '.git' in root or 'build' in root:
                continue
            
            rel_root = os.path.relpath(root, smdown_dir)
            
            # Determine which group based on path
            if 'Views' in rel_root:
                group_uuid = views_group_uuid
            elif 'ViewModels' in rel_root:
                group_uuid = viewmodels_group_uuid
            elif 'Models' in rel_root:
                group_uuid = models_group_uuid
            elif 'Services' in rel_root:
                group_uuid = services_group_uuid
            elif 'Downloader' in rel_root:
                group_uuid = downloader_group_uuid
            elif 'Utils' in rel_root:
                group_uuid = utils_group_uuid
            elif 'Resources' in rel_root:
                group_uuid = resources_group_uuid
            else:
                group_uuid = app_group_uuid

            for file in sorted(files):
                if file.endswith('.swift'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, smdown_dir)
                    self.add_source_file(rel_path, group_uuid)

        # Add Info.plist
        info_plist_uuid = self.create_file_reference('Info.plist', 'text.plist.xml')
        self.objects[app_group_uuid]['children'].insert(0, info_plist_uuid)

        # Add Assets.xcassets
        if os.path.exists(os.path.join(smdown_dir, 'Resources', 'Assets.xcassets')):
            assets_uuid = self.create_file_reference('Resources/Assets.xcassets', 'folder.assetcatalog')
            assets_build = self.create_build_file(assets_uuid)
            self.resource_build_files.append(assets_build)
            self.objects[resources_group_uuid]['children'].append(assets_uuid)

        # Create PBXNativeTarget
        self.objects[target_uuid] = {
            'isa': 'PBXNativeTarget',
            'buildConfigurationList': build_config_list_target_uuid,
            'buildPhases': [sources_phase_uuid, frameworks_phase_uuid, resources_phase_uuid],
            'buildRules': [],
            'dependencies': [],
            'name': self.project_name,
            'productName': self.project_name,
            'productReference': product_uuid,
            'productType': 'com.apple.product-type.application'
        }

        # Build phases
        self.objects[sources_phase_uuid] = {
            'isa': 'PBXSourcesBuildPhase',
            'buildActionMask': 2147483647,
            'files': self.source_build_files,
            'runOnlyForDeploymentPostprocessing': 0
        }

        self.objects[frameworks_phase_uuid] = {
            'isa': 'PBXFrameworksBuildPhase',
            'buildActionMask': 2147483647,
            'files': [],
            'runOnlyForDeploymentPostprocessing': 0
        }

        self.objects[resources_phase_uuid] = {
            'isa': 'PBXResourcesBuildPhase',
            'buildActionMask': 2147483647,
            'files': self.resource_build_files,
            'runOnlyForDeploymentPostprocessing': 0
        }

        # Build configurations - Project level
        self.objects[debug_config_uuid] = {
            'isa': 'XCBuildConfiguration',
            'buildSettings': {
                'ALWAYS_SEARCH_USER_PATHS': 'NO',
                'CLANG_ANALYZER_NONNULL': 'YES',
                'CLANG_CXX_LIBRARY': 'libc++',
                'CLANG_ENABLE_MODULES': 'YES',
                'CLANG_ENABLE_OBJC_ARC': 'YES',
                'COPY_PHASE_STRIP': 'NO',
                'DEBUG_INFORMATION_FORMAT': 'dwarf',
                'ENABLE_STRICT_OBJC_MSGSEND': 'YES',
                'ENABLE_TESTABILITY': 'YES',
                'GCC_OPTIMIZATION_LEVEL': '0',
                'GCC_PREPROCESSOR_DEFINITIONS': ['DEBUG=1', '$(inherited)'],
                'MACOSX_DEPLOYMENT_TARGET': '14.0',
                'MTL_ENABLE_DEBUG_INFO': 'INCLUDE_SOURCE',
                'ONLY_ACTIVE_ARCH': 'YES',
                'SDKROOT': 'macosx',
                'SWIFT_ACTIVE_COMPILATION_CONDITIONS': 'DEBUG',
                'SWIFT_OPTIMIZATION_LEVEL': '-Onone',
                'SUPPORTED_PLATFORMS': 'macosx',
                'SUPPORTS_MACCATALYST': 'NO',
                'SUPPORTS_MAC_DESIGNATED_FOR_IPAD': 'NO'
            },
            'name': 'Debug'
        }

        self.objects[release_config_uuid] = {
            'isa': 'XCBuildConfiguration',
            'buildSettings': {
                'ALWAYS_SEARCH_USER_PATHS': 'NO',
                'CLANG_ANALYZER_NONNULL': 'YES',
                'CLANG_CXX_LIBRARY': 'libc++',
                'CLANG_ENABLE_MODULES': 'YES',
                'CLANG_ENABLE_OBJC_ARC': 'YES',
                'COPY_PHASE_STRIP': 'NO',
                'DEBUG_INFORMATION_FORMAT': 'dwarf-with-dsym',
                'ENABLE_NS_ASSERTIONS': 'NO',
                'ENABLE_STRICT_OBJC_MSGSEND': 'YES',
                'MACOSX_DEPLOYMENT_TARGET': '14.0',
                'MTL_ENABLE_DEBUG_INFO': 'NO',
                'SDKROOT': 'macosx',
                'SWIFT_COMPILATION_MODE': 'wholemodule',
                'SWIFT_OPTIMIZATION_LEVEL': '-O',
                'SUPPORTED_PLATFORMS': 'macosx',
                'SUPPORTS_MACCATALYST': 'NO',
                'SUPPORTS_MAC_DESIGNATED_FOR_IPAD': 'NO'
            },
            'name': 'Release'
        }

        # Build configurations - Target level
        self.objects[debug_target_config_uuid] = {
            'isa': 'XCBuildConfiguration',
            'buildSettings': {
                'ASSETCATALOG_COMPILER_APPICON_NAME': 'AppIcon',
                'CODE_SIGN_STYLE': 'Automatic',
                'COMBINE_HIDPI_IMAGES': 'YES',
                'CURRENT_PROJECT_VERSION': '1',
                'GENERATE_INFOPLIST_FILE': 'YES',
                'INFOPLIST_FILE': f'{self.project_name}/Info.plist',
                'INFOPLIST_KEY_LSApplicationCategoryType': 'public.app-category.utilities',
                'INFOPLIST_KEY_NSDownloadsFolderUsageDescription': 'SMdown needs access to save downloaded videos to your Downloads folder',
                'INFOPLIST_KEY_NSPhotoLibraryUsageDescription': 'SMdown needs access to save downloaded videos to your Photos library',
                'LD_RUNPATH_SEARCH_PATHS': ['$(inherited)', '@executable_path/../Frameworks'],
                'MARKETING_VERSION': '1.0',
                'PRODUCT_BUNDLE_IDENTIFIER': self.bundle_id,
                'PRODUCT_NAME': '$(TARGET_NAME)',
                'SWIFT_EMIT_LOC_STRINGS': 'YES',
                'SWIFT_VERSION': '5.0'
            },
            'name': 'Debug'
        }

        self.objects[release_target_config_uuid] = {
            'isa': 'XCBuildConfiguration',
            'buildSettings': {
                'ASSETCATALOG_COMPILER_APPICON_NAME': 'AppIcon',
                'CODE_SIGN_STYLE': 'Automatic',
                'COMBINE_HIDPI_IMAGES': 'YES',
                'CURRENT_PROJECT_VERSION': '1',
                'GENERATE_INFOPLIST_FILE': 'YES',
                'INFOPLIST_FILE': f'{self.project_name}/Info.plist',
                'INFOPLIST_KEY_LSApplicationCategoryType': 'public.app-category.utilities',
                'INFOPLIST_KEY_NSDownloadsFolderUsageDescription': 'SMdown needs access to save downloaded videos to your Downloads folder',
                'INFOPLIST_KEY_NSPhotoLibraryUsageDescription': 'SMdown needs access to save downloaded videos to your Photos library',
                'LD_RUNPATH_SEARCH_PATHS': ['$(inherited)', '@executable_path/../Frameworks'],
                'MARKETING_VERSION': '1.0',
                'PRODUCT_BUNDLE_IDENTIFIER': self.bundle_id,
                'PRODUCT_NAME': '$(TARGET_NAME)',
                'SWIFT_EMIT_LOC_STRINGS': 'YES',
                'SWIFT_VERSION': '5.0'
            },
            'name': 'Release'
        }

        # Configuration lists
        self.objects[build_config_list_project_uuid] = {
            'isa': 'XCConfigurationList',
            'buildConfigurations': [debug_config_uuid, release_config_uuid],
            'defaultConfigurationIsVisible': 0,
            'defaultConfigurationName': 'Release'
        }

        self.objects[build_config_list_target_uuid] = {
            'isa': 'XCConfigurationList',
            'buildConfigurations': [debug_target_config_uuid, release_target_config_uuid],
            'defaultConfigurationIsVisible': 0,
            'defaultConfigurationName': 'Release'
        }

        # PBXProject
        self.objects[project_uuid] = {
            'isa': 'PBXProject',
            'attributes': {
                'BuildIndependentTargetsInParallel': 1,
                'LastSwiftUpdateCheck': 1500,
                'LastUpgradeCheck': 1500,
                'TargetAttributes': {
                    target_uuid: {
                        'CreatedOnToolsVersion': 15.0
                    }
                }
            },
            'buildConfigurationList': build_config_list_project_uuid,
            'compatibilityVersion': 'Xcode 14.0',
            'developmentRegion': 'en',
            'hasScannedForEncodings': 0,
            'knownRegions': ['en', 'Base'],
            'mainGroup': main_group_uuid,
            'productRefGroup': products_group_uuid,
            'projectDirPath': '',
            'projectRoot': '',
            'targets': [target_uuid]
        }

        # Create final project
        project = {
            'archiveVersion': 1,
            'classes': {},
            'objectVersion': 56,
            'objects': self.objects,
            'rootObject': project_uuid
        }

        # Write project file
        project_dir = os.path.join(output_path, f'{self.project_name}.xcodeproj')
        os.makedirs(project_dir, exist_ok=True)

        project_file = os.path.join(project_dir, 'project.pbxproj')
        with open(project_file, 'wb') as f:
            plistlib.dump(project, f)

        # Create workspace
        workspace_dir = os.path.join(project_dir, 'project.xcworkspace')
        os.makedirs(workspace_dir, exist_ok=True)

        workspace_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AppKitFunctions</key>
	<dict>
		<key>WKAppKitBuildIntegrationClass</key>
		<string>XCDistributedBuildWorkspaceBuildIntegration</string>
	</dict>
	<key>WorkspaceSharedData</key>
	<dict>
		<key>IDEWorkspaceSharedSettings_HasUserSettings</key>
		<false/>
	</dict>
</dict>
</plist>
'''
        workspace_file = os.path.join(workspace_dir, 'contents.xcworkspacedata')
        with open(workspace_file, 'w') as f:
            f.write(workspace_content)

        print(f"✅ Xcode project generated successfully!")
        print(f"📁 Location: {project_file}")
        print(f"\nTo open in Xcode:")
        print(f"   cd {output_path}")
        print(f"   open {self.project_name}.xcodeproj")

if __name__ == '__main__':
    generator = XcodeProjectGenerator(
        project_name='SMDown_M',
        bundle_id='com.smdown.app'
    )
    generator.generate('/Users/initialh/Projects/smdown/SMDown_M')
