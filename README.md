# Glitch3d

Glitch3d is an automated render library that uses glitching techniques applied to 3D meshes. The original intent was to focus on 3D glitching techniques and morphed into a render bot.

You can read a bit more about where it come from [here](http://pascal.cc/blog/glitches) and see it living [there](https://twitter.com/glitchdemon).

<img src="https://raw.githubusercontent.com/pskl/glitch3d/master/fixtures/examples/demo.jpg" width="400">

This gem uses the Blender Python API to produces renders headlessly and leverages the raytracing engine Cycles to get optimal renders. Calls made to the Blender API have been tested with versions 2.78 and 2.79.

Cycles rendering engine does not support GLSL shaders so the shader library is using a node-based system but could be extended to serialize materials in the Open Shading Language.

## :warning: Warning

Setting `BLENDER_EXECUTABLE_PATH` in your environment is required. In general this gem relies on the presence of Python and Blender on the host machine. I am very aware this is not standard practice and plan to split components later down the road but this proves convenient for now.

## Installation

Add this line to your application's Gemfile:

```ruby
gem 'glitch3d'
```

And then execute:

    $ bundle

Or install it yourself as:

    $ gem install glitch3d

## Usage

- `glitch3d file.obj`

CLI Options:
- `mode` : (localized|default|none) => glitching strategy
- `shots-number` : integer representing the number of - images desired (with animate: false)
- `quality` : (high: 2000 x 2000|low 200 x 200) default: low => size of the render
- `animate` : (true) default: false => Render .avi file
- `frames` : (default: 200) => number of frames for simulation

Renders (wether it is video or an image) will be output to `./renders` along with an export of the `.scene` file so that you can potentially fiddle with the resulting scene setup and adjust lights for instance.

## Examples

In your favorite terminal:

`glitch3d /path/to/model.obj --quality=high --mode=none --shots-number=12 --frames=100`
-> will fetch your .obj will and render 12 high quality visuals (in current folder under the folder called `renders`) of it without glitching it at all.

`glitch3d /path/to/model.obj --animate=true --frames=1000`
-> will render a video in .avi format long of 1000 frames

## Development

After checking out the repo, run `bin/setup` to install dependencies. Then, run `rake spec` to run the tests. You can also run `bin/console` for an interactive prompt that will allow you to experiment.

To install this gem onto your local machine, run `bundle exec rake install`. To release a new version, update the version number in `version.rb`, and then run `bundle exec rake release`, which will create a git tag for the version, push git commits and tags, and push the `.gem` file to [rubygems.org](https://rubygems.org).

## Roadmap

- extract fixtures management from gem
- allow fixtures to be scraped from online resources such as [Thingiverse](https://www.thingiverse.com/)
- use Blender Compositor feature to streamline post-processing
- use realtime Eevee engine to visualize intermediate renders

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/pskl/glitch3d. This project is intended to be a safe, welcoming space for collaboration, and contributors are expected to adhere to the [Contributor Covenant](http://contributor-covenant.org) code of conduct.

## License

Copyright © 217 PSKL <hello@pascal.cc>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.

NOTE: Above license is for the code part only. Some of the materials used as fixtures could be copyrighted (models and textures). Please be careful.
