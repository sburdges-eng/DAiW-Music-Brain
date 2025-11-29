/**
 * DAiW_Buffer.cpp - Implementation of audio buffer wrapper
 *
 * Most functionality is in the header (template class), but this file
 * provides explicit template instantiations for common types to
 * reduce compilation time and ensure proper linkage.
 */

#include "DAiW_Buffer.h"

namespace daiw {
namespace memory {

// Explicit template instantiations for common types
template class DAiW_Buffer<float>;
template class DAiW_Buffer<double>;
template class DAiW_Buffer<int32_t>;
template class DAiW_Buffer<int16_t>;
template class DAiW_Buffer<uint8_t>;

} // namespace memory
} // namespace daiw
