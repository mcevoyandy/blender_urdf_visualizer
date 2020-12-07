# Blender URDF Viewer

Blender v2.90.1

## Development Setup in Linux

Create a symlink to this repository in your local config:

```
cd ~/.config/blender/2.90/scripts/addons
ln -s ~/git/blender_urdf_visualizer blender_urdf_visualizer
```

Enable the Add-on in Blender:

1. Open Blender
1. Navigate to `Edit > Preferences`
1. Select `Add-ons > Testing`
1. Enable `Object: URDF`

**NOTES:**
1. During development, you may need to disable the Add-on and re-enable it for it to load properly.
1. To see all of the output from the console, launch blender from the command line.
