# frozen_string_literal: true
module Glitch3d
  module FindAndReplace
    def alter_vertices(vertices_objects_array)
      @target = rand(9).to_s
      @replacement = rand(9).to_s
      vertices_objects_array.each do |v|
        find_and_replace(v)
      end
      vertices_objects_array
    end

    def alter_faces(faces_objects_array, vertices_objects_array)
      faces_objects_array
    end

    def find_and_replace(vertex)
      vertex.x = vertex.x.to_s.tr(@target, @replacement).to_f
      vertex.y = vertex.y.to_s.tr(@target, @replacement).to_f
      vertex.z = vertex.z.to_s.tr(@target, @replacement).to_f
    end
  end
end
