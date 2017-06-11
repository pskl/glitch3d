# frozen_string_literal: true
module Glitch3d
  module Localized
    def alter_vertices(vertices_objects_array)
      sorted_array = vertices_objects_array.sort do |v1, v2| 
        rand_attr = v1.rand_attr
        v1.send(rand_attr) <=> v2.send(rand_attr)
      end
      (VERTEX_GLITCH_ITERATION_RATIO * sorted_array.size).to_i.times do |_|
        random_element(target(sorted_array)).fuck
      end
      sorted_array
    end

    def alter_faces(faces_objects_array, vertices_objects_array)
      (FACE_GLITCH_ITERATION_RATIO * faces_objects_array.count).to_i.times do |_|
        random_element(faces_objects_array).fuck(random_element(target(vertices_objects_array)))
      end
      faces_objects_array
    end

    def selected_area(vertices_objects_array)
      Vertex.subset(x: :positive?, y: :positive?, z: :positive?, vertex_list: vertices_objects_array)
    end

    def target(vertices_objects_array)
      @target ||= selected_area(vertices_objects_array)
    end
  end
end
