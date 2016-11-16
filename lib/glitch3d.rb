require "glitch3d/version"

module Glitch3d

  attr_accessor :target_file
  attr_accessor :source_file

  def process_model(source_file)
    @source_file = source_file
    @target_file = source_file + '_glitched.obj'
    create_glitched_file(alter_vertices(read_source(source_file)))
  end

  # @param path String
  # @return vertice_lines Array
  def read_source(path)
    File.open(path, 'r') do |f|
      source_file_content = f.readlines
      puts source_file_content.size
      vertice_lines = source_file_content.select { |s| s[0] == 'v' }
      return vertice_lines
    end
  end

  # @param data Array
  # @return Array
  def alter_vertices(vertice_lines)
    random_index = rand(0..vertice_lines.size - 1)
    row = vertice_lines[random_index].split(' ')
    vertice_lines[random_index] = alter_row(row)
    vertice_lines
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
    new_row
  end

  # @param data Array
  # @return file_path String
  def create_glitched_file(content)
    File.open(target_file, 'w') do |f|
      content.unshift('# Data corrupted with 3dglitch script')
      f.write content
    end
  end
end
