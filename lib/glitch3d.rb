require "glitch3d/version"

module Glitch3d
  attr_accessor :target_file
  attr_accessor :source_file

  attr_accessor :vertices_lines
  attr_accessor :faces_lines

  def process_model(source_file)
    @source_file = source_file.end_with?('.obj') ? source_file : (source_file + '.obj')
    @target_file = source_file + '_glitched.obj'
    create_glitched_file(glitch(read_source(@source_file)))
  end

  # @param path String
  # @return Hash
  def read_source(path)
    File.open(path, 'r') do |f|
      source_file_content = f.readlines
      puts 'Source file linecount: ' + source_file_content.size.to_s
      vertices_lines = source_file_content.select { |s| s[0] == 'v' }
      faces_lines = source_file_content.select { |s| s[0] == 'f' }
      {
        vertices: vertices_lines,
        faces: faces_lines
      }
    end
  end

  def glitch(file_hash_content)
    {
      vertices: alter_vertices(file_hash_content[:vertices]),
      faces: alter_faces(file_hash_content[:faces])
    }
  end

  # @param data Array
  # @return Array
  def alter_vertices(vertices_lines)
    random_index = rand(0..vertices_lines.size - 1)
    row = vertices_lines[random_index].split(' ')
    vertices_lines[random_index] = alter_row(row)
    vertices_lines
  end

  def alter_faces(faces_lines)
    faces_lines
  end

  # @param row Array
  # @return new_row Array
  def alter_row(row)
    new_row = {
      x: row[1] .to_f,
      y: row[2].to_f,
      z: row[3].to_f
    }
    new_row[[:x, :y, :z].sample] += 0.5
    "v #{new_row[:x]} #{new_row[:y]} #{new_row[:z]}"
  end

  # @param data Hash
  # @return file_path String
  def create_glitched_file(content_hash)
    File.open(target_file, 'w') do |f|
      f.puts '# Data corrupted with 3dglitch script'
      f.puts ''
      f.puts content_hash[:vertices]
      f.puts ''
      f.puts content_hash[:faces]
    end
  end
end
