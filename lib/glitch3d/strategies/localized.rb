module Glitch3d
  module Localized
    def alter_vertices(vertices_objects_array)
      array = selected_area(vertices_objects_array)
      (VERTEX_GLITCH_ITERATION_RATIO * array.size).to_i.times do |_|
        random_element(array).fuck
      end
      array
    end

    def alter_faces(faces_objects_array, vertex_objects_array)
      (FACE_GLITCH_ITERATION_RATIO * faces_objects_array.count).to_i.times do |_|
        random_element(faces_objects_array).fuck(random_element(vertex_objects_array))
      end
      faces_objects_array
    end

    def selected_area(vertices_objects_array)
      Vertex.subset(x: :positive?, y: :positive?, z: :positive?, vertex_list: vertices_objects_array)
    end
  end
end
