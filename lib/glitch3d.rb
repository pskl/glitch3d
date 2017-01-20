require "glitch3d/version"

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
    create_glitched_file(glitch(read_source(source_file)))
    render(target_file)
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
      vertices_list << Vertex.new(x: v[1], y: v[2], z: v[3])
    end
    puts 'Furthest point'
    vertices_list
  end

  def build_faces(faces_string_array)
    faces_list = []
    faces_string_array.map do |sf|
      f = sf.split(' ')
      next if f.length <= 3
      faces_list << Face.new(v1: f[1].to_i, v2: f[2].to_i, v3: f[3].to_i)
    end
    faces_list
  end

  def glitch(file_hash_content)
    {
      vertices: alter_vertices(file_hash_content[:vertices]),
      faces: alter_faces(file_hash_content[:faces])
    }
  end

  def alter_vertices(vertices_objects_array)
    (VERTEX_GLITCH_ITERATION_RATIO * @vertex_count).to_i.times do |_|
      alter_vertice_row(random_element(vertices_objects_array))
    end
    vertices_objects_array
  end

  def random_element(array)
    array[rand(0..array.size - 1)]
  end

  def alter_faces(faces_objects_array)
    (FACE_GLITCH_ITERATION_RATIO * @face_count).to_i.times do |_|
      alter_face_row(random_element(faces_objects_array))
    end
    faces_list
  end

  def rand_vertex_glitch_offset
    rand(-VERTEX_GLITCH_OFFSET..VERTEX_GLITCH_OFFSET)
  end

  def rand_vertex_reference
    rand(1..@vertex_count - 1)
  end

  def create_glitched_file(content_hash)
    File.open(target_file, 'w') do |f|
      f.puts '# Data corrupted with glitch3D script'
      f.puts ''
      f.puts 'g Glitch3D'
      f.puts ''
      f.puts content_hash[:vertices].map(&:to_s)
      f.puts ''
      f.puts content_hash[:faces].map(&:to_s)
    end
  end

  def render(file_path)
    args = [
      BLENDER_EXECUTABLE_PATH,
      '-b',
      '-P',
      RENDERING_SCRIPT_PATH,
      '--',
      '-f',
      file_path
    ]
    unless system(*args)
      fail 'Make sure Blender is correctly installed'
    end
  end
end
