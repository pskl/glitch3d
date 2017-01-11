require "glitch3d/version"

module Glitch3d
  attr_accessor :target_file
  attr_accessor :source_file

  VERTEX_GLITCH_ITERATION_RATIO = 0.2
  VERTEX_GLITCH_OFFSET = 0.6

  FACE_GLITCH_ITERATION_RATIO = 0.2
  FACE_GLITCH_OFFSET = 0.6

  BLENDER_EXECUTABLE_PATH = "/Applications/blender-2.78-OSX_10.6-x86_64/blender.app/Contents/MacOS/blender"
  RENDERING_SCRIPT_PATH = "lib/glitch3d/rendering_script.py"

  def process_model(source_file)
    @vertices_list = []
    @faces_list = []
    @source_file = source_file
    @base_file_name = source_file.gsub(/.obj/, '')
    @target_file = @base_file_name + '_glitched.obj'
    create_glitched_file(glitch(read_source(@source_file)))
    render(@target_file)
  end

  # @param path String
  # @return Hash
  def read_source(path)
    File.open(@source_file, 'r') do |f|
      source_file_content = f.readlines
      {
        vertices: build_vertices(source_file_content.select { |s| s[0..1] == 'v ' }),
        faces: build_faces(source_file_content.select { |s| s[0..1] == 'f ' })
      }
    end
  end

  # @param Array<String>
  def build_vertices(vertices_string_array)
    vertices_list = []
    vertices_string_array.map do |sv|
      v = sv.split(' ')
      vertices_list<< Vertex.new(x: v[1], y: v[2], z: v[3])
    end
    vertices_list
  end

  def build_faces(faces_string_array)
    faces_list = []
    faces_string_array.map do |sf|
      f = sf.split(' ')
      faces_list<< Face.new(v1: f[1], v2: f[2], v3: f[3])
    end
    faces_list
  end

  # @param
  #
  # @return Vertex
  def furthest_vertex(vertices_list)
    furthest_vertices = [
      vertices_list.max_by { |v| v.x },
      vertices_list.max_by { |v| v.y },
      vertices_list.max_by { |v| v.z }
    ]
    max_coord = [
      furthest_vertices[0].x,
      furthest_vertices[1].y,
      furthest_vertices[2].z
    ].max
    furthest_vertices.find { |v| v.x == max_coord || v.y == max_coord || v.z == max_coord }
  end

  def glitch(file_hash_content)
    {
      vertices: alter_vertices(file_hash_content[:vertices]),
      faces: alter_faces(file_hash_content[:faces])
    }
  end

  # @param data Array
  # @return Array
  def alter_vertices(vertices_list)
    (VERTEX_GLITCH_ITERATION_RATIO * @vertex_count).to_i.times do |_|
      random_index = rand(0..vertices_list.size - 1)
      row = vertices_list[random_index]
      vertices_list[random_index] = alter_vertice_row(row)
    end
    50.times do
      vertices_list[rand(0..vertices_lines.size - 1)] = vertices_list[rand(0..vertices_list.size - 1)]
    end
    vertices_list
  end

  def alter_faces(faces_list)
    (FACE_GLITCH_ITERATION_RATIO * @face_count).to_i.times do |_|
      random_index = rand(0..faces_list.size - 1)
      row = faces_list[random_index].split(' ')
      next if row.length <= 3
      faces_list[random_index] = alter_face_row(row)
    end
    faces_list
  end

  # @param row Array
  # @return new_row Array
  def alter_vertice_row(row)
    rand_offset = rand(-VERTEX_GLITCH_OFFSET..VERTEX_GLITCH_OFFSET)
    new_row = {
      x: row[1].to_f,
      y: row[2].to_f,
      z: row[3].to_f
    }
    new_row[[:x, :y, :z].sample] += rand_offset
    Vertex.new(x: new_row[:x], y: new_row[:y], z: new_row[:z])
  end

  # @param row Array
  # @return new_row Array
  def alter_face_row(row)
    new_row = {
      v1: row[1]&.split('/')&.first&.to_i,
      v2: row[2]&.split('/')&.first&.to_i,
      v3: row[3]&.split('/')&.first&.to_i,
      v4: row[4]&.split('/')&.first&.to_i,
      v5: row[5]&.split('/')&.first&.to_i,
      v6: row[6]&.split('/')&.first&.to_i
    }.select { |_, v| !v.nil? }
    target_edge = new_row.keys.sample
    vertice_reference = new_row[target_edge]
    new_vertice_reference = rand(1..@vertex_count - 1)
    new_row[target_edge] = new_vertice_reference
    "f #{new_row.values.join(' ').squeeze(' ')}"
  end

  # @param data Hash
  # @return file_path String
  def create_glitched_file(content_hash)
    File.open(target_file, 'w') do |f|
      f.puts '# Data corrupted with 3dglitch script'
      f.puts ''
      f.puts "g #{@source_file}"
      f.puts ''
      f.puts content_hash[:vertices]
      f.puts ''
      f.puts content_hash[:faces]
    end
  end

  # @param uri file_path
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
