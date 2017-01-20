class Face
  attr_accessor :v1, :v2, :v3

  def initialize
    @v1 = v1
    @v2 = v2
    @v3 = v3
  end

  def to_s
    "v #{x} #{y} #{z}"
  end

  def alter(face_object)
    f = face_object.dup
    f.send("#{[:v1, :v2, :v3].sample}=", rand_vertex_reference)
    f
  end
end
