class Face
  attr_accessor :v1, :v2, :v3

  def initialize(v1, v2, v3)
    @v1 = v1
    @v2 = v2
    @v3 = v3
  end

  def to_s
    return nil unless !v1.nil? && !v2.nil? && !v3.nil?
    "f #{v1.index} #{v2.index} #{v3.index}"
  end

  def rand_attr
    [:v1, :v2, :v3].sample
  end

  def fuck(new_vertex)
    send("#{rand_attr}=", new_vertex)
  end
end
