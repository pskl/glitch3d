require "glitch3d/version"
require "glitch3d/vertex"
require "glitch3d/face"

module Glitch3d
  VERTEX_GLITCH_ITERATION_RATIO = 0.2
  VERTEX_GLITCH_OFFSET = 0.6

  FACE_GLITCH_ITERATION_RATIO = 0.2
  FACE_GLITCH_OFFSET = 0.6

  BLENDER_EXECUTABLE_PATH = "/Applications/blender-2.78-OSX_10.6-x86_64/blender.app/Contents/MacOS/blender".freeze
  RENDERING_SCRIPT_PATH = "lib/glitch3d/rendering_script.py".freeze

  def process_model(source_file)
    source_file = source_file
    base_file_name = source_file.gsub(/.obj/, '')
    target_file = base_file_name + '_glitched.obj'
    furthest = create_glitched_file(glitch(read_source(source_file)), target_file)
    render(target_file, furthest)
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
      {
        vertices: build_vertices(source_file_content.select { |s| s[0..1] == 'v ' }),
        faces: build_faces(source_file_content.select { |s| s[0..1] == 'f ' })
      }
    end
  end

  def build_vertices(vertices_string_array)
    vertices_list = []
    vertices_string_array.map do |sv|
      v = sv.split(' ')
      vertices_list << Vertex.new(v[1].to_f, v[2].to_f, v[3].to_f)
    end
    puts 'Furthest point: ' + Vertex.furthest(vertices_list).to_s
    vertices_list
  end

  def build_faces(faces_string_array)
    faces_list = []
    faces_string_array.map do |sf|
      f = sf.split(' ')
      next if f.length <= 3
      faces_list << Face.new(f[1].to_i, f[2].to_i, f[3].to_i)
    end
    faces_list
  end

  def glitch(file_hash_content)
    {
      vertices: alter_vertices(file_hash_content[:vertices]),
      faces: alter_faces(file_hash_content[:faces], file_hash_content[:vertices])
    }
  end

  def alter_vertices(vertices_objects_array)
    (VERTEX_GLITCH_ITERATION_RATIO * vertices_objects_array.size).to_i.times do |_|
      random_element(vertices_objects_array).fuck
    end
    vertices_objects_array
  end

  def random_element(array)
    array[rand(0..array.size - 1)]
  end

  def alter_faces(faces_objects_array, vertex_objects_array)
    (FACE_GLITCH_ITERATION_RATIO * vertex_objects_array.count).to_i.times do |_|
      random_element(faces_objects_array).fuck(vertex_objects_array)
    end
    faces_objects_array
  end

  def create_glitched_file(content_hash, target_file)
    File.open(target_file, 'w') do |f|
      f.puts '# Data corrupted with glitch3D script'
      f.puts ''
      f.puts 'g Glitch3D'
      f.puts ''
      f.puts content_hash[:vertices].map(&:to_s)
      f.puts ''
      f.puts content_hash[:faces].map(&:to_s)
    end
    Vertex.furthest(content_hash[:vertices])
  end

  def render(file_path, furthest)
    args = [
      BLENDER_EXECUTABLE_PATH,
      '-b',
      '-P',
      RENDERING_SCRIPT_PATH,
      '--',
      '-f',
      file_path,
      '-u',
      furthest.max.to_s,
      '-n',
      4.to_s
    ]
    unless system(*args)
      fail 'Make sure Blender is correctly installed'
    end
  end
end
