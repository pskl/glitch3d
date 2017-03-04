require "glitch3d/version"
require "glitch3d/objects/vertex"
require "glitch3d/objects/face"
require "glitch3d/strategies/default"
require "glitch3d/strategies/localized"
require "pry"

module Glitch3d
  VERTEX_GLITCH_ITERATION_RATIO = 0.001
  VERTEX_GLITCH_OFFSET = 1

  FACE_GLITCH_ITERATION_RATIO = 0.0
  FACE_GLITCH_OFFSET = 0.5
  BOUNDARY_LIMIT = 4 # Contain model within 2x2x2 cube

  BLENDER_EXECUTABLE_PATH = ENV['BLENDER_EXECUTABLE_PATH'].freeze
  RENDERING_SCRIPT_PATH = "lib/glitch3d/bpy/rendering.py".freeze

  def process_model(source_file)
    raise 'Set Blender executable path in your env variables before using glitch3d' unless BLENDER_EXECUTABLE_PATH.present?
    args = Hash[ARGV.join(' ').scan(/--?([^=\s]+)(?:=(\S+))?/)]
    self.class.include infer_strategy(args["mode"] || 'default')
    @quality = args["quality"] || 'low'
    source_file = source_file
    base_file_name = source_file.gsub(/.obj/, '')
    target_file = base_file_name + '_glitched.obj'
    boundaries = create_glitched_file(glitch(read_source(source_file)), target_file)
    render(target_file, boundaries, args["shots-number"] || 6) unless args["no-render"]
  end

  def infer_strategy(mode)
    return Glitch3d::Default if mode.nil?
    {
      default: Glitch3d::Default,
      localized: Glitch3d::Localized
    }[mode.to_sym]
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

  def create_glitched_file(content_hash, target_file)
    boundaries = Vertex.boundaries(content_hash[:vertices])
    puts boundaries.to_s
    while rescale_needed?(boundaries)
      content_hash[:vertices] = Vertex.rescale(content_hash[:vertices], (boundaries.flatten.map(&:abs).max.abs - BOUNDARY_LIMIT).abs)
      boundaries = Vertex.boundaries(content_hash[:vertices])
    end
    boundaries = Vertex.boundaries(content_hash[:vertices])
    puts boundaries.to_s
    File.open(target_file, 'w') do |f|
      f.puts '# Data corrupted with glitch3D script'
      f.puts '# Boundaries: ' +  boundaries.to_s
      f.puts ''
      f.puts 'g Glitch3D'
      f.puts ''
      f.puts content_hash[:vertices].map(&:to_s)
      f.puts ''
      f.puts content_hash[:faces].map(&:to_s).compact
    end
    boundaries
  end

  def rescale_needed?(boundaries)
    boundaries.flatten.map(&:abs).max.abs > BOUNDARY_LIMIT
  end

  def render(file_path, boundaries, shots_number)
    args = [
      BLENDER_EXECUTABLE_PATH,
      '-b',
      '-P',
      RENDERING_SCRIPT_PATH,
      '--',
      '-f',
      file_path,
      '-n',
      shots_number.to_s,
      '-m',
      @quality
    ]
    unless system(*args)
      fail 'Make sure Blender is correctly installed'
    end
  end
end
