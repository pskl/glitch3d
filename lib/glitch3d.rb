# frozen_string_literal: true
require 'glitch3d/version'
require 'glitch3d/objects/vertex'
require 'glitch3d/objects/face'

Dir[File.dirname(__FILE__) + '/glitch3d/strategies/*.rb'].each { |file| require file }

module Glitch3d
  VERTEX_GLITCH_ITERATION_RATIO = 0.1
  VERTEX_GLITCH_OFFSET = 1

  FACE_GLITCH_ITERATION_RATIO = 0.1
  FACE_GLITCH_OFFSET = 0.5
  BOUNDARY_LIMIT = 4 # Contain model within 2x2x2 cube
  CHUNK_SIZE=20

  BLENDER_EXECUTABLE_PATH = ENV['BLENDER_EXECUTABLE_PATH'].freeze
  RENDERING_SCRIPT_PATH = File.dirname(__FILE__) + '/glitch3d/bpy/main.py'
  BASE_BLEND_FILE_PATH = File.dirname(__FILE__) + '/../fixtures/base.blend'

  def clean_model(source_file)
    self.class.include Glitch3d::None
    base_file_name = source_file.gsub(/.obj/, '')
    model_name = File.basename(source_file, '.obj')
    target_file = base_file_name + '.obj'
    create_glitched_file(glitch(read_source(source_file)), target_file, model_name)
  end

  # @param String source_file, 3d model file to take as input
  # @param Hash args, parameters { 'stuff' => 'shit' }
  def process_model(source_file, args)
    raise 'Make sure Blender is correctly installed' if BLENDER_EXECUTABLE_PATH.nil?
    return clean_model(source_file) if args['clean']
    source_file = random_fixture if source_file.nil?
    print_version if args.has_key?('version')
    raise 'Set Blender executable path in your env variables before using glitch3d' if BLENDER_EXECUTABLE_PATH.nil?
    self.class.include infer_strategy(args['mode'] || 'default')
    @quality = args['quality'] || 'low'
    source_file = source_file
    base_file_name = source_file&.gsub(/.obj/, '')
    model_name = File.basename(source_file, '.obj')
    target_file = base_file_name + '_glitched.obj'
    create_glitched_file(glitch(read_source(source_file)), target_file, model_name)
    render(args, target_file, args['shots-number'] || 6) unless args['no-render']
  end

  def print_version
    puts Glitch3d::VERSION
    return nil
  end

  def random_fixture
    @fixtures_path = File.dirname(__FILE__) + '/../fixtures'
    fixtures = []
    Dir.foreach(@fixtures_path) do |item|
      next if item == '.' or item == '..' or item.end_with?('_glitched.obj') or !item.end_with?('.obj')
      fixtures << @fixtures_path + '/' + item
    end
    fixtures.sample
  end

  def infer_strategy(mode)
    return [ Glitch3d::Default, Glitch3d::Duplication, Glitch3d::FindAndReplace, Glitch3d::Localized, Glitch3d::None].sample if mode.nil?
    begin
      return eval("Glitch3d::#{mode.to_s.gsub(/(?:_|^)(\w)/){$1.upcase}}")
    rescue
      raise "Strategy #{mode.to_s..gsub(/(?:_|^)(\w)/){$1.upcase}} not found"
    end
  end

  class << self
    def rand_vertex_glitch_offset
      rand(-VERTEX_GLITCH_OFFSET..VERTEX_GLITCH_OFFSET)
    end
  end

  private

  def read_source(path)
    File.open(path, 'r') do |f|
      source_file_content = f.readlines
      vertices_list = build_vertices(source_file_content.select { |s| s[0..1] == 'v ' })
      faces_list = build_faces(source_file_content.select { |s| s[0..1] == 'f ' }, vertices_list)
      {
        vertices: vertices_list,
        faces: faces_list
      }
    end
  end

  def build_vertices(vertices_string_array)
    vertices_list = []
    vertices_string_array.each_with_index.map do |sv, i|
      v = sv.split(' ')
      vertices_list << Vertex.new(v[1].to_f, v[2].to_f, v[3].to_f, i)
    end
    vertices_list
  end

  def build_faces(faces_string_array, vertices_list)
    faces_list = []
    faces_string_array.map do |sf|
      f = sf.split(' ')
      next if f.length <= 3
      faces_list << Face.new(
        vertices_list[f[1].to_i],
        vertices_list[f[2].to_i],
        vertices_list[f[3].to_i]
      )
    end
    faces_list
  end

  def glitch(file_hash_content)
    {
      vertices: alter_vertices(file_hash_content[:vertices]),
      faces: alter_faces(file_hash_content[:faces], file_hash_content[:vertices])
    }
  end

  def random_element(array)
    array[rand(0..array.size - 1)]
  end

  def create_glitched_file(content_hash, target_file, model_name)
    boundaries = Vertex.boundaries(content_hash[:vertices])
    puts boundaries.to_s
    while rescale_needed?(boundaries)
      content_hash[:vertices] = Vertex.rescale(content_hash[:vertices], (boundaries.flatten.map(&:abs).max.abs - BOUNDARY_LIMIT).abs)
      boundaries = Vertex.boundaries(content_hash[:vertices])
    end
    boundaries = Vertex.boundaries(content_hash[:vertices])
    File.open(target_file, 'w') do |f|
      f.puts '# Data corrupted with glitch3D script'
      f.puts model_name
      f.puts '# Boundaries: ' + boundaries.to_s
      f.puts ''
      f.puts "g 0_glitch3d"
      f.puts ''
      f.puts content_hash[:vertices].map(&:to_s)
      f.puts ''
      f.puts content_hash[:faces].map(&:to_s).compact
    end
  end

  def rescale_needed?(boundaries)
    boundaries.flatten.map(&:abs).max.abs > BOUNDARY_LIMIT
  end

  def render(initial_args, file_path, shots_number)
    args = [
      BLENDER_EXECUTABLE_PATH,
      '-b',
      BASE_BLEND_FILE_PATH,
      '-P',
      RENDERING_SCRIPT_PATH,
      '--',
      '-f',
      file_path,
      '-n',
      shots_number.to_s,
      '-m',
      @quality,
      '-p',
      File.dirname(__FILE__).to_s,
      '-a',
      initial_args['animate'].to_s.capitalize,
      '-d',
      initial_args['debug'].to_s.capitalize
    ]
    system(*args)
  end
end
