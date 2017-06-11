# frozen_string_literal: true
module Glitch3d
  module Default
    def alter_vertices(vertices_objects_array)
      (VERTEX_GLITCH_ITERATION_RATIO * vertices_objects_array.size).to_i.times do |_|
        random_element(vertices_objects_array).fuck
      end
      vertices_objects_array
    end

    def alter_faces(faces_objects_array, vertex_objects_array)
      # (FACE_GLITCH_ITERATION_RATIO * faces_objects_array.count).to_i.times do |_|
      #   random_element(faces_objects_array).fuck(random_element(vertex_objects_array))
      # end
      faces_objects_array
    end
  end
end
