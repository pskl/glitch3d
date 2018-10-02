# frozen_string_literal: true
module Glitch3d
  module Localized
    class NilSubSetError < StandardError; end

    class << self
      def alter_vertices(vertices_objects_array)
        sorted_array = vertices_objects_array.sort do |v1, v2|
          rand_attr = v1.rand_attr
          v1.send(rand_attr) <=> v2.send(rand_attr)
        end
        (VERTEX_GLITCH_ITERATION_RATIO * sorted_array.size).to_i.times do |_|
          target(sorted_array).sample.fuck
        end
        sorted_array
      end

      def alter_faces(faces_objects_array, vertices_objects_array)
        (FACE_GLITCH_ITERATION_RATIO * faces_objects_array.count).to_i.times do |_|
          faces_objects_array.sample.fuck(target(vertices_objects_array).sample)
        end
        faces_objects_array
      end

      def selected_area(vertices_objects_array)
        area = Vertex.subset(x: random_particularity, y: random_particularity, z: random_particularity, vertex_list: vertices_objects_array)
        raise NilSubSetError if area.nil? || area.empty?
        area
      end

      def random_particularity
        [:positive?, :negative?, :zero?].sample
      end

      def target(vertices_objects_array)
        selected_area(vertices_objects_array)
      end
    end
  end
end
