# coding: utf-8
# frozen_string_literal: true
lib = File.expand_path('../lib', __FILE__)
$LOAD_PATH.unshift(lib) unless $LOAD_PATH.include?(lib)
require 'glitch3d/version'

Gem::Specification.new do |spec|
  spec.name          = 'glitch3d'
  spec.version       = Glitch3d::VERSION
  spec.authors       = ['pskl']
  spec.email         = ['hello@pascal.cc']

  spec.summary       = 'Alter 3D models and renders pictures.'
  spec.description   = 'Glitch3D is a library designed to transform a 3D model randomly and render screenshots.'
  spec.homepage      = 'http://pascal.cc'
  spec.license       = 'MIT'

  # Prevent pushing this gem to RubyGems.org. To allow pushes either set the 'allowed_push_host'
  # to allow pushing to a single host or delete this section to allow pushing to any host.
  # if spec.respond_to?(:metadata)
  #   spec.metadata['allowed_push_host'] = "TODO: Set to 'http://mygemserver.com'"
  # else
  #   raise "RubyGems 2.0 or newer is required to protect against public gem pushes."
  # end

  spec.files         = `git ls-files -z`.split("\x0").reject { |f| f.match(%r{^(test|spec|features)/}) }
  spec.bindir        = 'bin'
  spec.executables   = ['glitch3d']
  spec.require_paths = ['lib']

  spec.add_development_dependency 'bundler', '~> 1.12'
  spec.add_development_dependency 'rake', '~> 10.0'
end
