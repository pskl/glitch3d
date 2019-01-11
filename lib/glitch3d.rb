# frozen_string_literal: true
require 'glitch3d/version'
require 'glitch3d/objects/vertex'
require 'glitch3d/objects/face'

Dir[File.dirname(__FILE__) + '/glitch3d/strategies/*.rb'].each { |file| require file }

module Glitch3d
  class ProcessError < StandardError; end

  VERTEX_GLITCH_ITERATION_RATIO = 0.0001.freeze
  VERTEX_GLITCH_OFFSET = 1.freeze

  FACE_GLITCH_ITERATION_RATIO = 0.0001.freeze
  FACE_GLITCH_OFFSET = 0.5.freeze
  BOUNDARY_LIMIT = 3.freeze # Contain model within BOUNDARY_LIMITxBOUNDARY_LIMITxBOUNDARY_LIMIT cube
  CHUNK_SIZE = 20.freeze
  DEFAULT_SHOTS_NUMBER = 4.freeze
  STRATEGIES = [
    Glitch3d::Default,
    Glitch3d::Duplication,
    Glitch3d::FindAndReplace,
    Glitch3d::Localized,
    Glitch3d::None
  ].freeze

  BLENDER_EXECUTABLE_PATH = ENV['BLENDER_EXECUTABLE_PATH'].freeze
  RENDERING_SCRIPT_PATH = File.dirname(__FILE__) + '/glitch3d/bpy/main.py'
  BASE_BLEND_FILE_PATH = File.dirname(__FILE__) + '/../fixtures/base.blend'
  BENCHMARK_ARGS = {
    'quality' => 'high',
    'normals' => false,
    'width' => 1000.to_s,
    'height' => 1000.to_s,
    'debug' => 'false',
    'canvas' => 'empty',
    'animate' => 'false',
    'post-process' => 'false'
  }

  ASCII_TITLE = "
  ██████╗ ██╗     ██╗████████╗ ██████╗██╗  ██╗██████╗ ██████╗
  ██╔════╝ ██║     ██║╚══██╔══╝██╔════╝██║  ██║╚════██╗██╔══██╗
  ██║  ███╗██║     ██║   ██║   ██║     ███████║ █████╔╝██║  ██║
  ██║   ██║██║     ██║   ██║   ██║     ██╔══██║ ╚═══██╗██║  ██║
  ╚██████╔╝███████╗██║   ██║   ╚██████╗██║  ██║██████╔╝██████╔╝
   ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═════╝ ╚═════╝
                                                               "
  def clean_model(source_file)
    self.class.include Glitch3d::None
    base_file_name = source_file.gsub(/.obj/, '')
    model_name = File.basename(source_file, '.obj')
    target_file = base_file_name + '.obj'
    create_glitched_file(glitch(read_source(source_file)), target_file, model_name)
  end

  def benchmark_strategies(source_file, base_file_name, model_name)
    require 'benchmark'
    Benchmark.bm do |x|
      STRATEGIES.each do |s|
        new_model_name = model_name + "_#{s.to_s.downcase.gsub(/::/, '_')}"
        target_file = new_model_name + '_glitched.obj'
        x.report s do
          create_glitched_file(
            glitch(read_source(source_file), s),
            target_file,
            new_model_name
          )
        end
      end
    end
    STRATEGIES.each do |s|
      new_model_name = model_name + "_#{s.to_s.downcase.gsub(/::/, '_')}"
      target_file = new_model_name + '_glitched.obj'
      render(BENCHMARK_ARGS, target_file, 1)
    end
  end

  # @param String source_file, 3d model file to take as input
  # @param Hash args, parameters { 'stuff' => 'shit' }
  def process_model(source_file, args)
    raise 'Make sure Blender is correctly installed' if BLENDER_EXECUTABLE_PATH.nil?
    @seed = args['seed'] ? args['seed'].to_i : rand(1000)
    srand @seed
    puts "Random seed: #{@seed}"
    puts ASCII_TITLE
    puts Glitch3d::VERSION
    return clean_model(source_file) if args['clean']
    source_file = random_fixture if source_file.nil?
    print_version if args.has_key?('version')
    raise 'Set Blender executable path in your env variables before using glitch3d' if BLENDER_EXECUTABLE_PATH.nil?
    source_file = source_file
    base_file_name = source_file&.gsub(/.obj/, '')
    model_name = File.basename(source_file, '.obj')
    target_file = base_file_name + '_glitched.obj'
    puts "Target ~> #{target_file}"
    return benchmark_strategies(source_file, base_file_name, model_name) if args['benchmark']
    create_glitched_file(
      glitch(read_source(source_file), infer_strategy(args['mode'])),
      target_file,
      model_name
    )
    render(args, target_file, args['shots-number'] || DEFAULT_SHOTS_NUMBER) unless args['no-render']
  end

  # Print version number
  # @return [String, nil]
  def print_version
    puts Glitch3d::VERSION
    return nil
  end

  # Fetch random model from fixtures folder
  # @return [String]
  def random_fixture
    @fixtures_path = File.dirname(__FILE__) + '/../fixtures/models'
    fixtures = []
    Dir.foreach(@fixtures_path) do |item|
      next if item == '.' or item == '..' or item.end_with?('_glitched.obj') or !item.end_with?('.obj')
      fixtures << @fixtures_path + '/' + item
    end
    fixtures.sample
  end

  # @param mode [String] name of strategy
  # @return [Glitch3d::Strategy]
  def infer_strategy(mode)
    if !mode
      mode_chosen = STRATEGIES.sample
      puts "Strategy defaulting to #{mode_chosen}"
      return mode_chosen
    end
    puts "Using #{mode}"
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

  def glitch(file_hash_content, strategy)
    {
      vertices: strategy.public_send(:alter_vertices, file_hash_content[:vertices]),
      faces: strategy.public_send(:alter_faces, file_hash_content[:faces], file_hash_content[:vertices])
    }
  end

  def create_glitched_file(content_hash, target_file, model_name)
    boundaries = Vertex.boundaries(content_hash[:vertices])
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
      f.puts "g 0_glitch3d_#{model_name}"
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
      initial_args['quality'] || 'low',
      '-p',
      File.dirname(__FILE__).to_s,
      '-a',
      initial_args['animate'].to_s.capitalize,
      '-d',
      initial_args['debug'].to_s.capitalize,
      '-frames',
      initial_args['frames'] || 100.to_s,
      '-normals',
      initial_args['normals'].to_s.capitalize,
      '-width',
      initial_args['width'] || 2000.to_s,
      '-eight',
      initial_args['height'] || 2000.to_s,
      '-canvas',
      initial_args['canvas'] || nil.to_s,
      '-assets',
      initial_args['assets'] || nil.to_s,
      '--post-process',
      initial_args['post-process'].to_s.capitalize,
      '--webhook',
      initial_args['webhook'] || nil.to_s,
      '--seed',
      @seed.to_s,
      '--python-exit-code',
      1.to_s
    ]
    raise(ProcessError, "bpy run failed, enable --debug=true for Python debugging") unless system(*args)
  end
end
