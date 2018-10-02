# frozen_string_literal: true
module Glitch3d
  module Duplication
    class << self
      def alter_vertices(vertices_objects_array)
        shuffle_vertices(vertices_objects_array)
      end

      def alter_faces(faces_objects_array, vertex_objects_array)
        faces_objects_array
      end

      def shuffle_vertices(array)
        rand(3..10).times do
          rand_index1 = rand(0..array.size - 1)
          rand_index2 = rand(0..array.size - 1)
          array[rand_index1], array[rand_index2] = array[rand_index2], array[rand_index1]
        end
        array
      end
    end
  end
end
